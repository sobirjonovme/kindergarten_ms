from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .api_endpoints import (AttendanceListAPIView, CreateAttendanceAPIView,
                            CustomTokenObtainPairView, MyProfileAPIView,
                            UserCreateAPIView, UserMonthlyAttendanceAPIView)

app_name = "users"

urlpatterns = [
    path("token/", CustomTokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("profile/", MyProfileAPIView.as_view(), name="my-profile"),
    # attendance
    path("attendance/create/", CreateAttendanceAPIView.as_view(), name="attendance-create"),
    path("attendance/list/", AttendanceListAPIView.as_view(), name="attendance-list"),
    path("<int:pk>/monthly-attendance/", UserMonthlyAttendanceAPIView.as_view(), name="user-monthly-attendance"),
    # users management
    path("create-user/", UserCreateAPIView.as_view(), name="user-create"),
]
