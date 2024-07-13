from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.users.models import User
from apps.users.tasks import send_user_info_to_hikvision


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "middle_name",
            "face_id",
            "gender",
            "type",
            "tuition_fee",
            "work_start_time",
            "work_end_time",
            "salary",
            "organization",
            "educating_group",
            "parents_tg_ids",
        )

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)

        try:
            instance.clean()
        except DjangoValidationError as e:
            raise ValidationError(detail=serializers.as_serializer_error(e))

        send_user_info_to_hikvision.delay(instance.id)

        return instance
