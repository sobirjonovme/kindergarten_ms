from datetime import datetime

import requests
from django.utils import timezone
from requests.auth import HTTPDigestAuth

from apps.common.models import FaceIDSettings
from apps.common.services.logging import LoggingException, TelegramLogging
from apps.users.choices import FaceIDLogTypes
from apps.users.models import FaceIDLog, User


class AttendanceService:
    def __init__(self, ip_address, username, password, last_sync_time, log_type):
        self.base_url = ip_address
        self.username = username
        self.password = password
        self.log_type = log_type

        sync_time_str = timezone.localtime(last_sync_time).isoformat()
        self.last_sync_time = sync_time_str

        # Get the current local time
        current_time = timezone.localtime()
        # Format the time without microseconds
        formatted_time = current_time.strftime("%Y-%m-%dT%H:%M:%S%z")
        # Adjust the timezone offset format from +0500 to +05:00
        formatted_time = formatted_time[:-2] + ":" + formatted_time[-2:]
        self.end_time = formatted_time

    def save_last_sync_time(self, last_event_time):
        if not last_event_time:
            return

        time_obj = datetime.fromisoformat(last_event_time)
        face_id_settings = FaceIDSettings.get_solo()

        if self.log_type == FaceIDLogTypes.ENTER:
            face_id_settings.enter_device_last_sync_time = time_obj
        elif self.log_type == FaceIDLogTypes.EXIT:
            face_id_settings.exit_device_last_sync_time = time_obj

        face_id_settings.save()

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
            timeout=40,
        )

        if res.status_code != 200:
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
                user_id = info.get("employeeNoString")
                serial_no = info.get("serialNo")

                if not user_id:
                    continue

                user = User.objects.filter(id=user_id).first()
                if not user:
                    # Log error and notify admin about missing user without stopping the process
                    exception = LoggingException(
                        message=str(info),
                        extra_kwargs={
                            "info": "User not found in database",
                            "user_id": user_id,
                        },
                    )
                    logging = TelegramLogging(exception)
                    logging.send_log_to_admin()
                    continue

                if serial_no and FaceIDLog.objects.filter(serial_no=serial_no).exists():
                    continue

                # add log record to list
                log_record_list.append(
                    FaceIDLog(
                        user=user,
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
        except Exception as e:
            # Log the exception and send the details to the admin
            logging = TelegramLogging(e)
            logging.send_log_to_admin()
