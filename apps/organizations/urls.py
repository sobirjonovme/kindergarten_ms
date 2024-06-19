from django.urls import path

from .api_endpoints import (EducatingGroupListAPIView, OrganizationListAPIView,
                            WorkCalendarCreateAPIView, WorkCalendarListAPIView,
                            WorkCalendarUpdateAPIView)

app_name = "organizations"

urlpatterns = [
    path("list/", OrganizationListAPIView.as_view(), name="organization-list"),
    path("educating-groups/", EducatingGroupListAPIView.as_view(), name="educating-group-list"),
    # Work Calendar
    path("work-calendar/create/", WorkCalendarCreateAPIView.as_view(), name="work-calendar-create"),
    path("work-calendar/list/", WorkCalendarListAPIView.as_view(), name="work-calendar-list"),
    path("work-calendar/<int:pk>/update/", WorkCalendarUpdateAPIView.as_view(), name="work-calendar-update"),
]
