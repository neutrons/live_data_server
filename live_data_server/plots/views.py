"""
    Definition of views
"""
import logging
import json
from django.shortcuts import render_to_response
from django.http import HttpResponseNotFound, JsonResponse, HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.views.decorators.cache import cache_page

from plots.models import PlotData
from . import view_util

def live_plot(request, instrument, run_id):
    """
        Test view for live plotting.
        @param instrument: instrument name
        @param run_id: run number
    """
    data_type_default = PlotData.get_data_type_from_string('html')
    data_type = request.GET.get('data_type', default=data_type_default)
    update_url = reverse('plots:update_as_%s' % PlotData.data_type_as_string(data_type),
                         kwargs={'instrument': instrument, 'run_id': run_id})
    client_key = view_util.generate_key(instrument, run_id)
    if client_key is not None:
        update_url += "?key=%s" % client_key
    template_values = {}
    template_values['data_type'] = data_type
    template_values['update_url'] = update_url
    return render_to_response('plots/live_plot.html',
                              template_values)

@view_util.check_key
@cache_page(15)
def update_as_json(request, instrument, run_id):
    """
        Ajax call to get JSON data
        @param instrument: instrument name
        @param run_id: run number
    """
    data_type = PlotData.get_data_type_from_string('json')
    plot_data = view_util.get_plot_data(instrument, run_id, data_type=data_type)

    if plot_data is None:
        error_msg = "No data available for %s %s" % (instrument, run_id)
        logging.error(error_msg)
        return HttpResponseNotFound(error_msg)

    json_data = json.loads(plot_data.data)
    return JsonResponse(json_data, safe=False)

@view_util.check_key
@cache_page(15)
def update_as_html(request, instrument, run_id):
    """
        Ajax call to get plot data as an html <div>
        @param instrument: instrument name
        @param run_id: run number
    """
    data_type = PlotData.get_data_type_from_string('html')
    plot_data = view_util.get_plot_data(instrument, run_id, data_type=data_type)

    if plot_data is None:
        error_msg = "No data available for %s %s" % (instrument, run_id)
        logging.error(error_msg)
        return HttpResponseNotFound(error_msg)

    response = HttpResponse(str(plot_data.data), content_type="text/html")
    response['Content-Length'] = len(response.content)
    return response

@csrf_exempt
def upload_plot_data(request, instrument, run_id):
    """
        Upload plot data
        @param instrument: instrument name
        @param run_id: run number
    """
    if request.method == 'POST' and 'file' in request.FILES:
        raw_data = request.FILES['file'].read()
        data_type_default = PlotData.get_data_type_from_data(raw_data)
        data_type = request.POST.get('data_type', default=data_type_default)
        view_util.store_plot_data(instrument, run_id, raw_data, data_type)
    else:
        return HttpResponseBadRequest()

    return HttpResponse()
