from django.db.models import Sum

from apps.accounting.choices import MonthlyPaymentTypes
from apps.accounting.models import MonthlyPayment
from apps.organizations.models import WorkCalendar
from apps.users.models import UserPresence


class WorkerSalaryCalculation:
    def __init__(self, worker, month_date):
        self.worker = worker
        self.month_date = month_date.replace(day=1)

    def calculate(self):
        month_date = self.month_date
        worker_full_salary = self.worker.salary

        if not worker_full_salary:
            return

        # check and get work calendar for the worker
        work_calendar = WorkCalendar.objects.filter(
            worker_type=self.worker.type, month__year=month_date.year, month__month=month_date.month
        ).first()
        if not work_calendar:
            return

        # calculate total present time and total working hours
        worker_presences = UserPresence.objects.filter(
            user=self.worker,
            date__year=month_date.year,
            date__month=month_date.month,
            date__day__in=work_calendar.work_days,
        )
        data = worker_presences.aggregate(
            total_present_time=Sum("present_time"),  # how many hours the employee worked
            total_working_hours=Sum("total_working_hours"),  # how many hours the employee should actually work
        )
        total_present_time = data.get("total_present_time") or 0  # real
        total_working_hours = data.get("total_working_hours") or 0  # in document
        total_present_days = worker_presences.count()  # real
        total_working_days = len(work_calendar.work_days)  # in document
        if total_working_hours == 0:
            salary = 0
        else:
            salary = float(worker_full_salary) * total_present_days / total_working_days
            salary = round(salary * total_present_time / total_working_hours, -2)

        # get or create monthly payment
        monthly_payment = MonthlyPayment.objects.filter(
            user=self.worker, paid_month__year=month_date.year, paid_month__month=month_date.month
        ).first()
        if not monthly_payment:
            monthly_payment = MonthlyPayment(
                type=MonthlyPaymentTypes.SALARY,
                user=self.worker,
                amount=0,
                paid_month=month_date,
                worked_hours=total_present_time,
                total_working_days=total_working_days,
                present_days=total_present_days,
                full_salary=worker_full_salary,
                calculated_salary=salary,
            )
            monthly_payment.save()
        else:
            monthly_payment.worked_hours = total_present_time
            monthly_payment.total_working_days = total_working_days
            monthly_payment.present_days = total_present_days
            monthly_payment.calculated_salary = salary
            monthly_payment.full_salary = worker_full_salary
            monthly_payment.save(
                update_fields=["worked_hours", "total_working_days", "present_days", "calculated_salary", "full_salary"]
            )
