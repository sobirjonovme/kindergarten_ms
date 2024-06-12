from rest_framework import serializers

from apps.accounting.serializers import MonthlyPaymentListSerializer
from apps.users.models import User


class UsersMonthlyPaymentListSerializer(serializers.ModelSerializer):
    monthly_payments = MonthlyPaymentListSerializer(many=True)
    present_days = serializers.IntegerField(read_only=True, allow_null=True)

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "middle_name",
            "type",
            "face_image",
            "present_days",
            "monthly_payments",
        )
        ref_name = "UsersMonthlyPaymentListSerializer"


class WorkerSalaryListSerializer(serializers.ModelSerializer):
    monthly_payments = MonthlyPaymentListSerializer(many=True)
    # present_days = serializers.IntegerField(read_only=True, allow_null=True)
    # worked_hours = serializers.IntegerField(read_only=True, allow_null=True)
    # total_working_hours = serializers.IntegerField(read_only=True, allow_null=True)
    # calculated_salary = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "middle_name",
            "type",
            "face_image",
            # "present_days",
            # "worked_hours",
            # "total_working_hours",
            # "calculated_salary",
            "monthly_payments",
        )
        ref_name = "WorkerSalaryMonthlyPaymentListSerializer"

    # def get_calculated_salary(self, obj):
    #     # TODO: create model to save old salary and calculate old monthly payment via that old salary
    #
    #     if obj.salary and obj.worked_hours and obj.total_working_hours:
    #         # calculate monthly salary for worker
    #         # round to the thousands room
    #         return round(obj.salary * obj.worked_hours / obj.total_working_hours, -2)
