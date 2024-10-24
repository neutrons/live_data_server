"""live_data_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  path(r'^blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, re_path
from django.views.generic.base import RedirectView

app_name = "live_data_server"

urlpatterns = [
    re_path(r"^admin/", admin.site.urls),
    re_path(r"^$", RedirectView.as_view(url="/plots/")),
    re_path(r"^plots/", include("apps.plots.urls", namespace="plots")),
]
