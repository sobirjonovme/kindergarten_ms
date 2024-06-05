import uuid

import requests
from django.conf import settings
from requests.auth import HTTPDigestAuth

from apps.common.services.logging import LoggingException, TelegramLogging
from apps.users.models import User


class UserInfoReceiver:
    def __init__(self, ip_address, username, password):
        self.base_url = ip_address
        self.username = username
        self.password = password

        self.auth = HTTPDigestAuth(username, password)

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
            print("Failed to download the image. Status code:", response.status_code)

    def _store_user_info_bulk(self):
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
                print("+++++++++++++++++++++++++++")
                # Process each info and store in database
                user_name = info.get("name")
                face_id = info.get("employeeNo")
                face_image_url = info.get("faceURL")
                print(face_id, " | ", user_name)

                if not face_image_url:
                    print("No face image URL")
                    continue

                image = self.download_user_face_image(image_url=face_image_url, user_name=user_name, user_id=face_id)

                if not image:
                    continue

                user = User.objects.filter(face_id=face_id).first()
                if not user:
                    # Log error and notify admin about missing user without stopping the process
                    exception = LoggingException(
                        message=str(info),
                        extra_kwargs={
                            "info": "User not found in database in UserInfoReceiver",
                            "face_id": face_id,
                        },
                    )
                    logging = TelegramLogging(exception)
                    logging.send_log_to_admin()
                    continue

                user.face_image = image
                user.save(update_fields=["face_image"])
                print(f"{user.id} | Successfully saved face image")

            if res_status == "OK":
                break

            search_position += 20

    def store_user_info_bulk(self):
        try:
            self._store_user_info_bulk()
        except Exception as e:
            print("==========================================")
            print(e)


if __name__ == "__main__":
    base_url = "http://192.168.100.82"
    username = "admin"
    password = "Hunter2003"

    user_info_receiver = UserInfoReceiver(base_url, username, password)
    user_info_receiver.store_user_info_bulk()
