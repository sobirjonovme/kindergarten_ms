from rest_framework import serializers

from .models import EducatingGroup, Organization


class OrganizationShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ("id", "name")


class EducatingGroupShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducatingGroup
        fields = ("id", "name")
