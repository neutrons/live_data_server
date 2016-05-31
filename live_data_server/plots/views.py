"""
    Definition of views
"""
import logging
from django.views.generic import View
from django.shortcuts import render_to_response
from django.http import JsonResponse, HttpResponse

from . import view_util

class LivePlotView(View):
    """
        Basic plot view
    """
    def get(self, request):
        template_values = {}
        template_values['plot_as_div'] = view_util.get_plot_as_div()
        template_values['as_div'] = 1 if 'as_div' in request.GET else 0
        return render_to_response('plots/plot_live.html',
                                  template_values)

def  plot_live_update(request):
    """
        Handle ajax call to update the live plot
    """
    if not request.is_ajax():
        logging.warning("Received non-ajax plot_live_update request")

    if 'as_div' in request.GET:
        return HttpResponse(view_util.get_plot_as_div())

    data = view_util.get_plot_as_json()
    # In order to allow non-dict objects to be serialized set the safe parameter to False
    return JsonResponse([data], safe=False)

def upload_plot_data(request):
    """
        Upload plot data
    """
    return HttpResponse('1')
