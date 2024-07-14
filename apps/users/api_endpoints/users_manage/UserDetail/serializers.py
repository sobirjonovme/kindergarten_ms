from rest_framework import serializers

from apps.organizations.serializers import (EducatingGroupShortSerializer,
                                            OrganizationShortSerializer)
from apps.users.models import User


class UserDetailSerializer(serializers.ModelSerializer):
    organization = OrganizationShortSerializer()
    educating_group = EducatingGroupShortSerializer()

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "middle_name",
            "face_image",
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
