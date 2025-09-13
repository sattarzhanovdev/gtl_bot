# gtl_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.views.static import serve
from django.urls import re_path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("gtl.urls")),
    # OpenAPI схема (json/yaml)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),

    # Swagger UI и Redoc, которые читают схему по url_name='schema'
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("", RedirectView.as_view(url="/static-app/")),
]

urlpatterns += [
    re_path(r"^static-app/$", serve, {"path": "index.html", "document_root": settings.BASE_DIR / "frontend"}),
]