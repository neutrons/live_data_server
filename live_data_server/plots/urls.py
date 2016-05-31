"""
    Define url structure
"""
from django.conf.urls import url
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='/plots/plot_live/')),
    url(r'^plot_live/$', views.LivePlotView.as_view(), name='plot_live'),
    url(r'^plot_live_update/$', views.plot_live_update, name='plot_live_update'),
]
