#pylint: disable=invalid-name, line-too-long
"""
    Define url structure
"""
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<instrument>[\w]+)/(?P<run_id>\d+)/$', views.live_plot, name='live_plot'),
    url(r'^(?P<instrument>[\w]+)/(?P<run_id>\d+)/update/json/$', views.update_as_json, name='update_as_json'),
    url(r'^(?P<instrument>[\w]+)/(?P<run_id>\d+)/update/html/$', views.update_as_html, name='update_as_html'),
    url(r'^(?P<instrument>[\w]+)/(?P<run_id>\d+)/upload_plot_data/$', views.upload_plot_data, name='upload_plot_data'),
]
