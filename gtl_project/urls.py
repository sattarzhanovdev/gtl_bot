# gtl_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.views.static import serve
from django.urls import re_path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("gtl.urls")),
    path("", RedirectView.as_view(url="/static-app/")),
]

urlpatterns += [
    re_path(r"^static-app/$", serve, {"path": "index.html", "document_root": settings.BASE_DIR / "frontend"}),
]