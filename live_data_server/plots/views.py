"""
    Definition of views
"""
import logging
import datetime
from django.shortcuts import render_to_response
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse

from plots.models import PlotData
from . import view_util

def live_plot(request, instrument, run_id):
    """
        Test view for live plotting.
        @param instrument: instrument name
        @param run_id: run number
    """
    data_type = request.GET.get('data_type', default=1)
    update_url = reverse('plots:live_plot_update',
                         kwargs={'instrument': instrument, 'run_id': run_id})
    update_url += '?data_type=%s' % data_type

    template_values = {}
    template_values['data_type'] = data_type
    template_values['update_url'] = update_url
    return render_to_response('plots/live_plots.html',
                              template_values)

def  live_plot_update(request, instrument, run_id):
    """
        Handle ajax call to update the live plot
        @param instrument: instrument name
        @param run_id: run number
    """
    if not request.is_ajax():
        logging.warning("Received non-ajax plot_live_update request")

    data_type = request.GET.get('data_type', default=1)
    plot_data = view_util.get_plot_data(instrument, run_id, data_type=data_type)

    if plot_data.is_div():
        return HttpResponse(plot_data.data)
    else:
        return JsonResponse([plot_data.data], safe=False)


@csrf_exempt
def upload_plot_data(request, instrument, run_id):
    """
        Upload plot data
        @param instrument: instrument name
        @param run_id: run number
    """
    if request.method == 'POST' and 'file' in request.FILES:
        raw_content = request.FILES['file'].read()
        data_type_default = PlotData.get_data_type_from_data(raw_content)
        data_type = request.POST.get('data_type', default=data_type_default)

        run_object = view_util.get_or_create_run(instrument, run_id)

        # Look for a data file and treat it differently
        data_entries = PlotData.objects.filter(data_run=run_object)
        if len(data_entries) > 0:
            plot_data = data_entries[0]
        else:
            # No entry was found, create one
            plot_data = PlotData()
            plot_data.data_type = data_type
            plot_data.data_run = run_object
            plot_data.timestamp = datetime.datetime.utcnow()

        plot_data.data = raw_content
        plot_data.save()
    else:
        return HttpResponseBadRequest()

    return HttpResponse()
