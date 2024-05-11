from django.contrib import admin

from .models import MonthlyPayment


# Register your models here.
@admin.register(MonthlyPayment)
class MonthlyPaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "type", "amount", "paid_month", "is_completed")
    list_display_links = ("id", "user")

    list_filter = ("type", "is_completed")
    search_fields = ("user__username", "user__first_name", "user__last_name", "user__middle_name")

    autocomplete_fields = ("user",)
    date_hierarchy = "paid_month"
    readonly_fields = ("created_at", "updated_at")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related("user")
        return qs
