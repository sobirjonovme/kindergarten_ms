from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
# from django.conf.urls.i18n import i18n_patterns
from django.urls import include, path, re_path

from core.swagger.schema import swagger_urlpatterns

urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path("api/v1/common/", include("apps.common.urls")),
    path("api/v1/accounting/", include("apps.accounting.urls")),
    path("api/v1/organizations/", include("apps.organizations.urls")),
    path("api/v1/users/", include("apps.users.urls")),
]

# urlpatterns += i18n_patterns(path("admin/", admin.site.urls))
urlpatterns += swagger_urlpatterns

if "rosetta" in settings.INSTALLED_APPS:
    urlpatterns += [re_path(r"^rosetta/", include("rosetta.urls"))]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
