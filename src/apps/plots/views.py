"""
Definition of views
"""

import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseNotFound
from django.utils import timezone
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt

from apps.plots.models import DATA_TYPES

from . import view_util


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
def update_as_html(request, instrument, run_id):  # noqa: ARG001
    """
    Ajax call to get plot data as an html <div>
    @param instrument: instrument name
    @param run_id: run number
    """
    plot_data = view_util.get_plot_data(instrument, run_id)

    if plot_data is None:
        error_msg = f"No data available for {instrument} {run_id}"
        logging.error(error_msg)
        return HttpResponseNotFound(error_msg)

    response = HttpResponse(str(plot_data.data), content_type="text/html")
    response["Content-Length"] = len(response.content)
    return response


@check_credentials
def _store(request, instrument, run_id):
    """
    Store plot data
    @param instrument: instrument name
    @param run_id: run number
    """
    if "file" in request.FILES:
        raw_data = request.FILES["file"].read().decode("utf-8")
        data_type = DATA_TYPES["html"]  # Always HTML now
        expiration_date = request.POST.get(
            "expiration_date",
            default=timezone.now() + timedelta(days=settings.LIVE_PLOT_EXPIRATION_TIME),
        )
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
    return _store(request, instrument, run_id)
