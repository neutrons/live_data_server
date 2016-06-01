#pylint: disable=invalid-name, line-too-long
"""
    Define url structure
"""
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<instrument>[\w]+)/(?P<run_id>\d+)/$', views.live_plot, name='live_plot'),
    url(r'^(?P<instrument>[\w]+)/(?P<run_id>\d+)/update/$', views.live_plot_update, name='live_plot_update'),
    url(r'^(?P<instrument>[\w]+)/(?P<run_id>\d+)/upload_plot_data/$', views.upload_plot_data, name='upload_plot_data'),
]
