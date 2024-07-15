from rest_framework import serializers

from apps.users.models import User


class UserCreateSerializer(serializers.ModelSerializer):
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

    def validate(self, data):
        user = User(**data)
        user.clean_fields_via_type()
        user.clean()

        return data
