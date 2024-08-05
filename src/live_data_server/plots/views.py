"""
Definition of views
"""

from datetime import timedelta
import json
import logging

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import dateformat, timezone
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt

# from live_data_server.config import DEFAULT_EXPIRATION_TIME
# from live_data_server.plots import view_util
from . import view_util

# from plots.models import DataRun, Instrument, PlotData
from .models import DataRun, Instrument, PlotData


DEFAULT_EXPIRATION_TIME = 365 * 3 # 3 years


def check_credentials(fn):
    """
    Function decorator to authenticate a request
    """

    def request_processor(request, *args, **kws):
        """
        Authentication process
        """
        if request.user.is_authenticated:
            return fn(request, *args, **kws)
        if request.method == "POST":
            username = request.POST.get("username")
            password = request.POST.get("password")
            request_user = authenticate(username=username, password=password)
            if request_user is not None and not request_user.is_anonymous:
                login(request, request_user)
                return fn(request, *args, **kws)
            else:
                return HttpResponse(status=401)
        else:
            return HttpResponse(status=401)

    return request_processor


@view_util.check_key
@cache_page(15)
def update_as_json(request, instrument, run_id):  # noqa: ARG001
    """
    Ajax call to get JSON data
    @param instrument: instrument name
    @param run_id: run number
    """
    data_type = PlotData.get_data_type_from_string("json")
    plot_data = view_util.get_plot_data(instrument, run_id, data_type=data_type)

    if plot_data is None:
        error_msg = f"No data available for {instrument} {run_id}"
        logging.error(error_msg)
        return HttpResponseNotFound(error_msg)

    json_data = json.loads(plot_data.data)
    return JsonResponse(json_data, safe=False)


@view_util.check_key
@cache_page(15)
def update_as_html(request, instrument, run_id):  # noqa: ARG001
    """
    Ajax call to get plot data as an html <div>
    @param instrument: instrument name
    @param run_id: run number
    """
    data_type = PlotData.get_data_type_from_string("html")
    plot_data = view_util.get_plot_data(instrument, run_id, data_type=data_type)

    if plot_data is None:
        error_msg = f"No data available for {instrument} {run_id}"
        logging.error(error_msg)
        return HttpResponseNotFound(error_msg)

    response = HttpResponse(str(plot_data.data), content_type="text/html")
    response["Content-Length"] = len(response.content)
    return response


@check_credentials
def _store(request, instrument, run_id=None, as_user=False):
    """
    Store plot data
    @param instrument: instrument name or user name
    @param run_id: run number
    @param as_user: if True, we will store as user data
    """
    # r =
    if "file" in request.FILES:
        raw_data = request.FILES["file"].read().decode("utf-8")
        data_type_default = PlotData.get_data_type_from_data(raw_data)
        data_type = request.POST.get("data_type", default=data_type_default)
        expiration_date = request.POST.get("expiration_date", default=None)
        if expiration_date is None:
            expiration_date = timezone.now() + timedelta(days=DEFAULT_EXPIRATION_TIME)
        if as_user:
            data_id = request.POST.get("data_id", default="")
            view_util.store_user_data(instrument, data_id, raw_data, data_type, expiration_date)
        else:
            view_util.store_plot_data(instrument, run_id, raw_data, data_type, expiration_date)
    else:
        return HttpResponse(status=400)

    return HttpResponse()


@csrf_exempt
def upload_plot_data(request, instrument, run_id):
    """
    Upload plot data
    @param instrument: instrument name
    @param run_id: run number
    """
    return _store(request, instrument, run_id, as_user=False)


@csrf_exempt
def upload_user_data(request, user):
    """
    Upload plot data
    @param user: user identifier to use
    """
    return _store(request, user, as_user=True)


@csrf_exempt
@check_credentials
def get_data_list(_, instrument):
    """
    Get a list of user data
    """
    instrument_object = get_object_or_404(Instrument, name=instrument.lower())
    data_list = []
    for item in DataRun.objects.filter(instrument=instrument_object):
        timestamp_local = timezone.localtime(item.created_on)
        timestamp_formatted = dateformat.DateFormat(timestamp_local).format(settings.DATETIME_FORMAT)
        expiration_local = timezone.localtime(item.expiration_date)
        expiration_formatted = dateformat.DateFormat(expiration_local).format(settings.DATETIME_FORMAT)
        data_list.append(
            dict(
                id=item.id,
                run_number=str(item.run_number),
                run_id=item.run_id,
                timestamp=item.created_on.isoformat(),
                created_on=timestamp_formatted,
                expiration_date=expiration_formatted,
                expired=True if expiration_local < timezone.now() else False,
            )
        )
    return JsonResponse(data_list, safe=False)
