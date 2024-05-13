from django.urls import path

from .api_endpoints import (CreateExpenseViewAPIView,
                            CreateMonthlyPaymentAPIView,
                            UpdateMonthlyPaymentAPIView,
                            UsersMonthlyPaymentListAPIView,
                            UserYearlyPaymentListAPIView)

app_name = "accounting"

urlpatterns = [
    # monthly payments
    path("monthly-payments/create/", CreateMonthlyPaymentAPIView.as_view(), name="monthly-payment-create"),
    path("monthly-payments/<int:pk>/update/", UpdateMonthlyPaymentAPIView.as_view(), name="monthly-payment-update"),
    path("monthly-payments/list/", UsersMonthlyPaymentListAPIView.as_view(), name="monthly-payment-list"),
    path(
        "monthly-payments/<int:user_id>/yearly/",
        UserYearlyPaymentListAPIView.as_view(),
        name="user-yearly-payment-list",
    ),
    # expenses
    path("expenses/create/", CreateExpenseViewAPIView.as_view(), name="expense-create"),
]
