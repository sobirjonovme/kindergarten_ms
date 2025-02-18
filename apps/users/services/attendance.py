import uuid
from datetime import datetime

import requests
from django.conf import settings
from django.utils import timezone
from requests.auth import HTTPDigestAuth

from apps.common.models import FaceIDSettings
from apps.common.services.logging import LoggingException, TelegramLogging
from apps.users.choices import FaceIDLogTypes
from apps.users.models import FaceIDLog, User
from apps.users.services.daily_presence import UserDailyPresence


def format_datetime_to_str(datetime_obj):
    # Format the time without microseconds
    formatted_time = datetime_obj.strftime("%Y-%m-%dT%H:%M:%S%z")
    # Adjust the timezone offset format from +0500 to +05:00
    formatted_time = formatted_time[:-2] + ":" + formatted_time[-2:]
    return formatted_time


class AttendanceService:
    def __init__(self, ip_address, username, password, last_sync_time, log_type):
        self.base_url = ip_address
        self.username = username
        self.password = password
        self.log_type = log_type

        self.auth = HTTPDigestAuth(username, password)

        last_sync_time = timezone.localtime(last_sync_time)
        sync_time_str = format_datetime_to_str(last_sync_time)
        self.last_sync_time = sync_time_str

        # Get the current local time
        current_time = timezone.localtime().replace(hour=23, minute=59, second=59)
        formatted_time = format_datetime_to_str(current_time)
        self.end_time = formatted_time

    def save_last_sync_time(self, last_event_time):
        if not last_event_time:
            return

        # time_obj = datetime.fromisoformat(last_event_time)
        time_obj = last_event_time
        face_id_settings = FaceIDSettings.get_solo()

        if self.log_type == FaceIDLogTypes.ENTER and time_obj > face_id_settings.enter_device_last_sync_time:
            face_id_settings.enter_device_last_sync_time = time_obj
            face_id_settings.save(update_fields=["enter_device_last_sync_time"])

        elif self.log_type == FaceIDLogTypes.EXIT and time_obj > face_id_settings.exit_device_last_sync_time:
            face_id_settings.exit_device_last_sync_time = time_obj
            face_id_settings.save(update_fields=["exit_device_last_sync_time"])

    def download_user_face_image(self, image_url, user_name):
        # Sending a GET request to download the image
        response = requests.get(image_url, auth=self.auth)

        # retrieve image extension
        image_extension = image_url.split(".")[-1]
        image_extension = image_extension.split("@")[0]

        user_name = user_name.replace(" ", "_")
        image_rel_path = f"face_id_logs/{user_name}_{uuid.uuid4().hex}.{image_extension}"

        # Check if the request was successful
        if response.status_code == 200:
            file_path = f"{settings.BASE_DIR}/media/{image_rel_path}"
            # Saving the image to a file
            with open(file_path, "wb") as f:
                f.write(response.content)
            return image_rel_path
        else:
            print("Failed to download the image. Status code:", response.status_code)

    def get_hikvision_device_response(self, start_time, end_time, search_position=0):
        res = requests.post(
            f"{self.base_url}/ISAPI/AccessControl/AcsEvent?format=json",
            json={
                "AcsEventCond": {
                    "searchID": "randomtxt",
                    "searchResultPosition": search_position,
                    "maxResults": 24,
                    "major": 0,
                    "minor": 0,
                    "startTime": start_time,
                    "endTime": end_time,
                    "timeReverseOrder": False,
                }
            },
            auth=HTTPDigestAuth(self.username, self.password),
            timeout=15,
        )

        if res.status_code != 200:
            print(res.text)
            raise LoggingException(
                message="Error in get_hikvision_device_response",
                extra_kwargs={"status_code": res.status_code, "info": "Bad status code from Hikvision device"},
            )

        return res.json()

    def retrieve_hikvision_device_info(self, start_time, end_time, search_position=0):
        data = self.get_hikvision_device_response(
            start_time=start_time,
            end_time=end_time,
            search_position=search_position,
        )
        if not data:
            raise LoggingException(
                message="Hikvision data is Empty",
                extra_kwargs={"info": "Hikvision data is Empty"},
            )

        acs_event = data.get("AcsEvent", {})
        total_matches = acs_event.get("totalMatches", 0)
        res_status = acs_event.get("responseStatusStrg", None)
        if total_matches == 0 or not res_status or res_status == "NO MATCH":
            return None

        return acs_event

    def _store_attendance_log(self):
        search_position = 0

        while True:
            acs_event = self.retrieve_hikvision_device_info(
                start_time=self.last_sync_time,
                end_time=self.end_time,
                search_position=search_position,
            )
            if not acs_event:
                break

            info_list = acs_event.get("InfoList", [])
            res_status = acs_event.get("responseStatusStrg", None)
            last_event_time = None

            log_record_list = []

            for info in info_list:  # noqa
                # Process each info and store in database
                last_event_time = info.get("time", None)
                last_event_time = datetime.fromisoformat(last_event_time)
                current_time = timezone.localtime()
                if current_time < last_event_time:
                    last_event_time = current_time

                face_id = info.get("employeeNoString")
                serial_no = info.get("serialNo")
                user_name = info.get("name")
                face_image_url = info.get("pictureURL")

                if not face_id:
                    continue

                user = User.objects.filter(face_id=face_id).first()
                if not user:
                    # Log error and notify admin about missing user without stopping the process
                    exception = LoggingException(
                        message=str(info),
                        extra_kwargs={
                            "info": "User not found in database",
                            "face_id": face_id,
                        },
                    )
                    logging = TelegramLogging(exception)
                    logging.send_log_to_admin()
                    continue

                if serial_no and FaceIDLog.objects.filter(serial_no=serial_no).exists():
                    continue

                # create user presence for the day
                UserDailyPresence(user, last_event_time.date()).create_user_presence()

                # download image
                image_path = None
                if face_image_url:
                    image_path = self.download_user_face_image(face_image_url, user_name)

                log_record_list.append(
                    FaceIDLog(
                        user=user,
                        image=image_path,
                        type=self.log_type,
                        time=last_event_time,
                        serial_no=serial_no,
                        log_data=info,
                    )
                )

            # store logs to database
            FaceIDLog.objects.bulk_create(log_record_list)
            self.save_last_sync_time(last_event_time)

            if res_status == "OK":
                break

            search_position += 24

    def store_attendance_log(self):
        try:
            self._store_attendance_log()
        # catch Connection error
        except requests.exceptions.ConnectionError as e:  # noqa
            pass
        except Exception as e:
            print("==========================================")
            print(e)
            # Log the exception and send the details to the admin
            logging = TelegramLogging(e)
            logging.send_log_to_admin()
