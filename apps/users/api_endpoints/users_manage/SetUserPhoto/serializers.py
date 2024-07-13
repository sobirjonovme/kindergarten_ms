from rest_framework import serializers

from apps.users.models import User
from apps.users.tasks import send_user_info_to_hikvision


class SetUserPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "face_image",
        )
        extra_kwargs = {
            "face_image": {
                "required": True,
                "allow_null": False,
            },
        }

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)

        send_user_info_to_hikvision.delay(instance.id)

        return instance
