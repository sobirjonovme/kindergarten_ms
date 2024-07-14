from rest_framework import serializers


class CheckFaceIDSerializer(serializers.Serializer):
    face_id = serializers.CharField(max_length=100, required=True)
    user_id = serializers.IntegerField(required=False, allow_null=True)
