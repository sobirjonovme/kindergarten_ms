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
    present_days = serializers.SerializerMethodField()
    worked_hours = serializers.SerializerMethodField()
    total_working_days = serializers.SerializerMethodField()
    calculated_salary = serializers.SerializerMethodField()
    full_salary = serializers.SerializerMethodField()

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
            "worked_hours",
            "total_working_days",
            "full_salary",
            "calculated_salary",
            "monthly_payments",
        )
        ref_name = "WorkerSalaryMonthlyPaymentListSerializer"

    def to_representation(self, instance):
        self.context["monthly_payment"] = instance.monthly_payments.first()
        return super().to_representation(instance)

    def get_present_days(self, obj):
        monthly_payment = self.context.get("monthly_payment")
        if not monthly_payment:
            return

        return monthly_payment.present_days

    def get_worked_hours(self, obj):
        monthly_payment = self.context.get("monthly_payment")
        if not monthly_payment:
            return

        return monthly_payment.worked_hours

    def get_total_working_days(self, obj):
        monthly_payment = self.context.get("monthly_payment")
        if not monthly_payment:
            return

        return monthly_payment.total_working_days

    def get_calculated_salary(self, obj):
        monthly_payment = self.context.get("monthly_payment")
        if not monthly_payment:
            return

        return monthly_payment.calculated_salary

    def get_full_salary(self, obj):
        monthly_payment = self.context.get("monthly_payment")
        if not monthly_payment:
            return

        return monthly_payment.full_salary
