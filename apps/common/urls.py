from django.urls import path

from .api_endpoints import (FrontendTranslationAPIView, HelperAPIView,
                            OverallStatisticsAPIView, VersionHistoryAPIView)

app_name = "common"

urlpatterns = [
    # common
    path("FrontendTranslations/", FrontendTranslationAPIView.as_view(), name="frontend-translations"),
    path("VersionHistory/", VersionHistoryAPIView.as_view(), name="version-history"),
    path("helper/", HelperAPIView.as_view(), name="helper"),
    # statistics
    path("overall-statistics/", OverallStatisticsAPIView.as_view(), name="overall-statistics"),
]
