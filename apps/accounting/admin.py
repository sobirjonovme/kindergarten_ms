from django.contrib import admin

from .models import Expense, ExpenseType, MonthlyPayment


# Register your models here.
@admin.register(MonthlyPayment)
class MonthlyPaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "type", "amount", "paid_month", "is_completed")
    list_display_links = ("id", "user")

    list_filter = ("type", "is_completed")
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
