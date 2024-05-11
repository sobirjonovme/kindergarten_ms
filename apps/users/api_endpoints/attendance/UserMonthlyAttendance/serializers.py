from rest_framework import serializers


class YearMonthSerializer(serializers.Serializer):
    year = serializers.IntegerField(required=True, allow_null=False)
    month = serializers.IntegerField(required=True, allow_null=False)
