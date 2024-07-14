from rest_framework import serializers

from apps.users.models import User


class UserListSerializer(serializers.ModelSerializer):
    enter_terminal_synced = serializers.BooleanField(read_only=True)
    exit_terminal_synced = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "middle_name",
            "face_image",
            "enter_terminal_synced",
            "exit_terminal_synced",
        )
