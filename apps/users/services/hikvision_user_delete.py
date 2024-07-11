import json
from pathlib import Path

import requests
from requests.auth import HTTPDigestAuth

from apps.common.services.logging import TelegramLogging
from apps.users.models import User

BASE_DIR = Path(__file__).resolve().parent


class UserDeleteService:
    def __init__(
        self,
        ip_address,
        username,
        password,
    ):
        self.base_url = ip_address
        self.username = username
        self.password = password

        self.auth = HTTPDigestAuth(username, password)

    def delete_user_from_hikvision_device(self, face_id):
        res = requests.put(
            f'{self.base_url}/ISAPI/AccessControl/UserInfo/Delete?format=json',
            json={
                "UserInfoDelCond":
                    {
                        "EmployeeNoList":
                            [
                                {"employeeNo": str(face_id)}
                            ]
                    }
            },
            auth=self.auth,
            timeout=20,
        )

    def get_users_info_response(self, search_position=0):
        res = requests.post(
            f"{self.base_url}/ISAPI/AccessControl/UserInfo/Search?format=json",
            json={
                "UserInfoSearchCond": {
                    "searchID": "randomtxt",
                    "maxResults": 20,
                    "searchResultPosition": search_position,
                }
            },
            auth=self.auth,
            timeout=15,
        )

        if res.status_code != 200:
            raise Exception("Bad Status")

        return res.json()

    def retrieve_users_info_list(self, search_position=0):
        data = self.get_users_info_response(search_position)
        if not data:
            raise Exception("Users info data is empty")

        user_info_search = data.get("UserInfoSearch", {})
        total_matches = user_info_search.get("totalMatches", 0)
        res_status = user_info_search.get("responseStatusStrg", None)
        if total_matches == 0 or not res_status or res_status == "NO MATCH":
            return None

        return user_info_search

    def _delete_unnecessary_users_from_hikvision_device(self):
        search_position = 0

        while True:
            user_info_search = self.retrieve_users_info_list(
                search_position=search_position,
            )
            if not user_info_search:
                break

            info_list = user_info_search.get("UserInfo", [])
            res_status = user_info_search.get("responseStatusStrg", None)

            for info in info_list:  # noqa
                # Process each info and store in database
                user_name = info.get("name")
                face_id = info.get("employeeNo")

                user = User.objects.filter(face_id=face_id).first()
                if not user:
                    # delete user from hikvision device
                    self.delete_user_from_hikvision_device(face_id)

                    print(f"{face_id} - {user_name} | Successfully deleted!")

            if res_status == "OK":
                break

            search_position += 20

    def delete_unnecessary_users_from_hikvision_device(self):
        try:
            self._delete_unnecessary_users_from_hikvision_device()
        # catch Connection error
        except requests.exceptions.ConnectionError as e:  # noqa
            pass
        except Exception as e:
            print("==========================================")
            print(e)


if __name__ == "__main__":
    base_url = "http://192.168.1.68"
    username = "admin"
    password = "techcraft2400"

    user_info_sender = UserDeleteService(base_url, username, password)
    user_info_sender.delete_unnecessary_users_from_hikvision_device()
