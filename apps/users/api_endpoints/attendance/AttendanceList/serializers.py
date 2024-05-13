from rest_framework import serializers

from apps.users.models import User


class AttendanceListSerializer(serializers.ModelSerializer):
    is_present = serializers.BooleanField(allow_null=True)

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "middle_name",
            "is_present",
        )


class DateSerializer(serializers.Serializer):
    date = serializers.DateField(required=True, allow_null=False)
