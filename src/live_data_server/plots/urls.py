"""
Define url structure
"""

from django.urls import re_path

from . import views

app_name = "plots"

urlpatterns = [
    re_path(r"^(?P<instrument>[\w]+)/(?P<run_id>\d+)/update/json/$", views.update_as_json, name="update_as_json"),
    re_path(r"^(?P<instrument>[\w]+)/(?P<run_id>\d+)/update/html/$", views.update_as_html, name="update_as_html"),
    re_path(
        r"^(?P<instrument>[\w]+)/(?P<run_id>\d+)/upload_plot_data/$", views.upload_plot_data, name="upload_plot_data"
    ),
    re_path(r"^(?P<user>[\w]+)/upload_user_data/$", views.upload_user_data, name="upload_user_data"),
    re_path(r"^(?P<instrument>[\w]+)/list/$", views.get_data_list, name="get_data_list"),
    re_path("get_all_runs", views.get_all_runs, name="get_all_runs"),
]
