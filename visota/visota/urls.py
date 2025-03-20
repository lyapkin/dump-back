"""
URL configuration for visota project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from seo.views import robots
from debug_toolbar.toolbar import debug_toolbar_urls

urlpatterns = [
    path("robots.txt", robots),
    path("admin/", admin.site.urls),
    path("smart_selects/", include("smart_selects.urls")),
    path("ckeditor5/", include("django_ckeditor_5.urls"), name="ck_editor_5_upload_file"),
    path("ckeditor/", include("ckeditor_uploader.urls")),
    path("api/vacancies/", include("apps.vacancies.urls")),
    path("api/projects/", include("apps.our_projects.urls")),
    path("api/promos/", include("apps.promos.urls")),
    path("api/request/", include("apps.requests.urls")),
]

urlpatterns += i18n_patterns(
    path("api/catalog/", include("apps.products.urls")),
    path("api/articles/", include("apps.blog.urls")),
    path("api/faq/", include("apps.faq.urls")),
    path("api/seo/", include("seo.urls")),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += debug_toolbar_urls()
