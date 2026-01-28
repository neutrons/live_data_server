"""
Define url structure
"""

from django.urls import re_path

from . import views

app_name = "plots"

urlpatterns = [
    re_path(r"^(?P<instrument>[\w]+)/(?P<run_id>\d+)/update/html/$", views.update_as_html, name="update_as_html"),
    re_path(
        r"^(?P<instrument>[\w]+)/(?P<run_id>\d+)/upload_plot_data/$", views.upload_plot_data, name="upload_plot_data"
    ),
]
