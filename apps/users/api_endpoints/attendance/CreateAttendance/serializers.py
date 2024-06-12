from rest_framework import serializers

from apps.users.models import User


class CreateAttendanceSerializer(serializers.Serializer):
    users = serializers.ListField(child=serializers.PrimaryKeyRelatedField(queryset=User.objects.all()))
