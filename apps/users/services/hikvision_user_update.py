import uuid

import requests
from django.conf import settings
from requests.auth import HTTPDigestAuth

from apps.common.services.logging import LoggingException, TelegramLogging
from apps.users.models import User


class UserImageReceiver:
    def __init__(self, ip_address, username, password, user_obj):
        self.base_url = ip_address
        self.username = username
        self.password = password
        self.user_obj = user_obj

        self.auth = HTTPDigestAuth(username, password)

    def get_user_info(self):
        res = requests.post(
            f'{self.base_url}/ISAPI/AccessControl/UserInfo/Search?format=json',
            json={
                "UserInfoSearchCond":
                    {
                        "searchID": "randomString",
                        "maxResults": 20,
                        "searchResultPosition": 0,
                        "EmployeeNoList":
                            [
                                {
                                    "employeeNo": str(self.user_obj.face_id)
                                }
                            ]
                    }
            },
            auth=self.auth,
            timeout=15,
        )

        if res.status_code != 200:
            raise Exception("Bad Status")

        return res.json()

    def download_user_face_image(self, image_url, user_name, user_id):
        # Sending a GET request to download the image
        response = requests.get(image_url, auth=self.auth)

        # retrieve image extension
        image_extension = image_url.split(".")[-1]
        image_extension = image_extension.split("@")[0]

        user_name = user_name.replace(" ", "_")
        image_rel_path = f"face_images/{user_id}_{user_name}_{uuid.uuid4().hex}.{image_extension}"

        # Check if the request was successful
        if response.status_code == 200:
            file_path = f"{settings.BASE_DIR}/media/{image_rel_path}"
            # Saving the image to a file
            with open(file_path, "wb") as f:
                f.write(response.content)
            return image_rel_path
        else:
            pass

    def _update_user_image_from_hikvision(self):
        user = self.user_obj

        data = self.get_user_info()
        search_info = data.get("UserInfoSearch", {})

        res_status = search_info.get("responseStatusStrg", None)
        if res_status == "NO MATCH":
            return

        info_list = search_info.get("UserInfo", [])
        if not info_list:
            return

        user_info = info_list[0]

        # Process each info and store in database
        user_name = user_info.get("name")
        face_id = user_info.get("employeeNo")
        face_image_url = user_info.get("faceURL")

        if not face_image_url or not face_id or str(face_id) != str(user.face_id):
            return

        image = self.download_user_face_image(image_url=face_image_url, user_name=user_name, user_id=face_id)

        if not image:
            return

        user.face_image = image
        user.save(update_fields=["face_image"])

    def update_user_image_from_hikvision(self):
        try:
            self._update_user_image_from_hikvision()
        except Exception as e:
            print("==========================================")
            print(e)


if __name__ == "__main__":
    base_url = "http://192.168.100.82"
    username = "admin"
    password = "Hunter2003"

    user_info_receiver = UserInfoReceiver(base_url, username, password)
    user_info_receiver.update_user_image_from_hikvision()
