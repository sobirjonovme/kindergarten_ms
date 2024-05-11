from django.urls import path

from .api_endpoints import (CreateMonthlyPaymentAPIView,
                            UpdateMonthlyPaymentAPIView,
                            UsersMonthlyPaymentListAPIView)

app_name = "accounting"

urlpatterns = [
    path("monthly-payments/create/", CreateMonthlyPaymentAPIView.as_view(), name="monthly-payment-create"),
    path("monthly-payments/<int:pk>/update/", UpdateMonthlyPaymentAPIView.as_view(), name="monthly-payment-update"),
    path("monthly-payments/list/", UsersMonthlyPaymentListAPIView.as_view(), name="monthly-payment-list"),
]
