from rest_framework import serializers

from .models import User


class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "middle_name",
            "face_image",
        )
