from django.urls import path

from .api_endpoints import EducatingGroupListAPIView, OrganizationListAPIView

app_name = "organizations"

urlpatterns = [
    path("list/", OrganizationListAPIView.as_view(), name="organization-list"),
    path("educating-groups/", EducatingGroupListAPIView.as_view(), name="educating-group-list"),
]
