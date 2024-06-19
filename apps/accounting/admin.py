from django.contrib import admin

from apps.accounting.tasks import calculate_salary
from apps.users.choices import UserTypes

from .models import Expense, ExpenseType, MonthlyPayment


# custom actions
def recalculate_salaries(modeladmin, request, queryset):
    workers_salaries = queryset.filter(user__type__in=[UserTypes.TEACHER, UserTypes.EDUCATOR])
    for obj in workers_salaries:
        calculate_salary.delay(user_id=obj.user_id, month_date=obj.paid_month)


# Register your models here.
@admin.register(MonthlyPayment)
class MonthlyPaymentAdmin(admin.ModelAdmin):
    actions = (recalculate_salaries,)
    list_display = (
        "id",
        "user",
        "type",
        "amount",
        "is_completed",
        "paid_month",
        "is_notified",
        "calculated_salary",
        "full_salary",
    )
    list_display_links = ("id", "user")

    list_filter = ("user__type", "is_completed", "type", "is_notified")
    search_fields = ("user__id", "user__username", "user__first_name", "user__last_name", "user__middle_name")

    autocomplete_fields = ("user",)
    date_hierarchy = "paid_month"
    readonly_fields = ("created_at", "updated_at")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related("user")
        return qs


@admin.register(ExpenseType)
class ExpenseTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    list_display_links = ("id", "name")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("id", "type", "amount", "date")
    list_display_links = ("id", "type")
    list_filter = ("type",)
    search_fields = ("type__name",)
    autocomplete_fields = ("type",)
    readonly_fields = ("created_at", "updated_at")
