import json
from pathlib import Path

import requests
from requests.auth import HTTPDigestAuth

from apps.common.services.logging import TelegramLogging
from apps.users.choices import FaceIDLogTypes

BASE_DIR = Path(__file__).resolve().parent


class UserInfoSender:
    def __init__(
        self,
        ip_address,
        username,
        password,
        device_type,
        user_obj=None,
        user_full_name=None,
        face_id=None,
        image_path=None,
    ):
        self.base_url = ip_address
        self.username = username
        self.password = password
        self.device_type = device_type
        self.user_obj = user_obj

        if user_obj:
            self.user_full_name = user_obj.generate_full_name()
            self.face_id = str(user_obj.face_id)
            self.image_path = user_obj.face_image.path
        else:
            self.user_full_name = user_full_name
            self.face_id = str(face_id)
            self.image_path = image_path

        self.auth = HTTPDigestAuth(username, password)

    def create_user(self):
        url = f"{self.base_url}/ISAPI/AccessControl/UserInfo/Record?format=json"
        json_data = {
            "UserInfo": {
                "employeeNo": self.face_id,
                "name": self.user_full_name,
                "userType": "normal",
                "Valid": {
                    "enable": False,
                    "beginTime": "2024-01-01T00:00:00",
                    "endTime": "2034-01-01T23:59:59",
                    "timeType": "local",
                },
                "doorRight": "1",
                "RightPlan": [{"doorNo": 1, "planTemplateNo": "1"}],
                # "gender": "male",
                # "localUIRight": False,  # is admin or not
            }
        }
        try:
            res = requests.post(url, json=json_data, auth=self.auth, timeout=10)
        except requests.exceptions.Timeout:
            return False, "Timeout error"

        if res.status_code == 200:
            return True, res.json()

        data_status = None
        if res.status_code == 400:
            try:
                res_data = res.json()
                data_status = res_data.get("subStatusCode", None)
            except Exception as e:  # noqa
                pass

        if data_status == "employeeNoAlreadyExist":
            return self.update_user_info()

        return False, res.text

    def update_user_info(self):
        url = f"{self.base_url}/ISAPI/AccessControl/UserInfo/Modify?format=json"
        json_data = {
            "UserInfo": {
                "employeeNo": self.face_id,
                "name": self.user_full_name,
                "userType": "normal",
                "Valid": {
                    "enable": False,
                    "beginTime": "2024-01-01T00:00:00",
                    "endTime": "2034-01-01T23:59:59",
                    "timeType": "local",
                },
                "doorRight": "1",
                "RightPlan": [{"doorNo": 1, "planTemplateNo": "1"}],
                # "gender": "male",
                # "localUIRight": False,  # is admin or not
            }
        }

        try:
            res = requests.put(url, json=json_data, auth=self.auth, timeout=10)
        except requests.exceptions.Timeout:
            return False, "Timeout error"

        if res.status_code == 200:
            return True, res.json()

        return False, res.text

    def upload_user_face_image(self):
        # URL of the API endpoint
        url = f"{self.base_url}/ISAPI/Intelligent/FDLib/FDSetUp?format=json"

        # Prepare the JSON data to be sent
        json_data = {"faceLibType": "blackFD", "FDID": "1", "FPID": self.face_id}

        # Prepare the file data
        image_name = Path(self.image_path).name
        files = {
            # The name "FaceDataRecord" and "img" should match the name expected by the server
            "FaceDataRecord": (None, json.dumps(json_data)),
            "img": (image_name, open(self.image_path, "rb"), "image/jpeg"),
        }

        try:
            res = requests.put(url, files=files, auth=self.auth, timeout=10)
        except Exception as e:
            # Log the exception and send the details to the admin
            logging = TelegramLogging(e)
            logging.send_log_to_admin()
            return False, str(e)

        # Close the file after the request
        files["img"][1].close()

        if res.status_code == 200:
            return True, res.json()

        return False, res.text

    def _send_user_data_to_hikvision(self):
        info_success, info_data = self.create_user()
        img_success, img_data = self.upload_user_face_image()

        user = self.user_obj
        if user:
            if self.device_type == FaceIDLogTypes.ENTER:
                user.is_enter_terminal_synced = info_success
                user.enter_terminal_sync_data = info_data
                user.is_enter_image_synced = img_success
                user.enter_image_sync_data = img_data
                user.save(
                    update_fields=[
                        "is_enter_terminal_synced",
                        "enter_terminal_sync_data",
                        "is_enter_image_synced",
                        "enter_image_sync_data",
                    ]
                )
            elif self.device_type == FaceIDLogTypes.EXIT:
                user.is_exit_terminal_synced = info_success
                user.exit_terminal_sync_data = info_data
                user.is_exit_image_synced = img_success
                user.exit_image_sync_data = img_data
                user.save(
                    update_fields=[
                        "is_exit_terminal_synced",
                        "exit_terminal_sync_data",
                        "is_exit_image_synced",
                        "exit_image_sync_data",
                    ]
                )

    def send_user_data_to_hikvision(self):
        try:
            self._send_user_data_to_hikvision()
        # catch Connection error
        except requests.exceptions.ConnectionError as e:  # noqa
            pass
        except Exception as e:
            print("==========================================")
            print(e)
            # Log the exception and send the details to the admin
            logging = TelegramLogging(e)
            logging.send_log_to_admin()


if __name__ == "__main__":
    base_url = "http://192.168.100.82"
    username = "admin"
    password = "Hunter2003"
    image_url = (
        "/home/sobirjonov_me/my_folder/my_progs/django/kindergarden_ms/media/face_images/photo_2023-06-24_18-37-37.jpg"
    )

    full_name = "Test 10 Updated"
    face_id = "10"

    user_info_sender = UserInfoSender(
        base_url, username, password, "ENTER", user_full_name=full_name, face_id=face_id, image_path=image_url
    )
    user_info_sender.send_user_data_to_hikvision()
