from django.db import models
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounting.choices import MonthlyPaymentTypes
from apps.accounting.models import MonthlyPayment
from apps.common.services.date_time import (calculate_average_attendance,
                                            get_last_month_date,
                                            get_month_days_count)
from apps.users.choices import UserTypes
from apps.users.models import FaceIDLog, User


class OverallStatisticsAPIView(APIView):
    def get(self, request):
        # ============================================================================ #
        # =====================   Calculate users count via type  ==================== #
        # ============================================================================ #
        users_counts = User.objects.all().aggregate(
            school_students=models.Count("id", filter=models.Q(type=UserTypes.STUDENT), distinct=True),
            teachers=models.Count("id", filter=models.Q(type=UserTypes.TEACHER), distinct=True),
            kindergarten_students=models.Count("id", filter=models.Q(type=UserTypes.KINDERGARTENER), distinct=True),
            kindergarten_educators=models.Count("id", filter=models.Q(type=UserTypes.EDUCATOR), distinct=True),
        )

        last_month_date = get_last_month_date()
        month_days_count = get_month_days_count(last_month_date)

        # ============================================================================ #
        # ===============   Calculate users average attendance via type  ============= #
        # ============================================================================ #

        face_id_logs = FaceIDLog.objects.filter(time__year=last_month_date.year, time__month=last_month_date.month)

        # calculate the kindergarteners attendance
        kindergarteners_logs = face_id_logs.filter(user__type=UserTypes.KINDERGARTENER)
        kindergartener_total_attendance = (
            kindergarteners_logs.values("time__date")
            .annotate(attendance=models.Count("user", distinct=True))
            .aggregate(total_attendance=models.Sum("attendance"))["total_attendance"]
        )
        # calculate the students attendance
        students_logs = face_id_logs.filter(user__type=UserTypes.STUDENT)
        student_total_attendance = (
            students_logs.values("time__date")
            .annotate(attendance=models.Count("user", distinct=True))
            .aggregate(total_attendance=models.Sum("attendance"))["total_attendance"]
        )
        # calculate the workers attendance
        workers_logs = face_id_logs.filter(user__type__in=UserTypes.get_worker_types())
        worker_total_attendance = (
            workers_logs.values("time__date")
            .annotate(attendance=models.Count("user", distinct=True))
            .aggregate(total_attendance=models.Sum("attendance"))["total_attendance"]
        )

        average_attendance = {
            "kindergartener": calculate_average_attendance(
                kindergartener_total_attendance, month_days_count, users_counts["kindergarten_students"]
            ),
            "school_student": calculate_average_attendance(
                student_total_attendance, month_days_count, users_counts["school_students"]
            ),
            "worker": calculate_average_attendance(
                worker_total_attendance,
                month_days_count,
                users_counts["teachers"] + users_counts["kindergarten_educators"],
            ),
        }

        # ============================================================================ #
        # ===============   Calculate average TUITION FEEs and SALARIES  ============= #
        # ============================================================================ #
        monthly_payments = MonthlyPayment.objects.filter(
            paid_month__year=last_month_date.year, paid_month__month=last_month_date.month
        )
        # calculate the average tuition fees
        tuition_fee_stats = monthly_payments.filter(type=MonthlyPaymentTypes.TUITION_FEE).aggregate(
            kindergarteners=models.Avg("amount", filter=models.Q(user__type=UserTypes.KINDERGARTENER)),
            school_students=models.Avg("amount", filter=models.Q(user__type=UserTypes.STUDENT)),
        )
        # calculate the average salaries
        salary_stats = monthly_payments.filter(type=MonthlyPaymentTypes.SALARY).aggregate(
            teachers=models.Avg("amount", filter=models.Q(user__type=UserTypes.TEACHER)),
            kindergarten_educators=models.Avg("amount", filter=models.Q(user__type=UserTypes.EDUCATOR)),
        )

        data = {
            "users_count": users_counts,
            "average_attendance": average_attendance,
            "average_tuition_fee": tuition_fee_stats,
            "average_salary": salary_stats,
        }

        return Response(data, status=status.HTTP_200_OK)


__all__ = ["OverallStatisticsAPIView"]
