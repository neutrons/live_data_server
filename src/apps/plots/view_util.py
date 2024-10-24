"""
Utility functions to support views.
"""

import hashlib
import logging
import sys
from datetime import datetime
from typing import Optional

from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone

from apps.plots.models import DataRun, Instrument, PlotData


def generate_key(instrument, run_id):
    """
    Generate a secret key for a run on a given instrument
    @param instrument: instrument name
    @param run_id: run number
    """
    if not hasattr(settings, "LIVE_PLOT_SECRET_KEY"):
        return None
    secret_key = settings.LIVE_PLOT_SECRET_KEY
    if len(secret_key) == 0:
        return None

    return hashlib.sha1(f"{instrument.upper()}{secret_key}{run_id}".encode("utf-8")).hexdigest()


def check_key(fn):
    """
    Function decorator to check whether a user is allowed
    to see a view.

    Usually used for AJAX calls.
    """

    def request_processor(request, instrument, run_id):
        """
        Decorator function
        """
        try:
            server_key = generate_key(instrument, run_id)
            if server_key is None:
                return fn(request, instrument, run_id)

            client_key = request.META.get("HTTP_AUTHORIZATION")

            # getting the client_key from request.GET.get("key") should be
            # removed after WebMon/WebRef supports Authorization request header
            if client_key is None:
                client_key = request.GET.get("key")

            if client_key == server_key:
                return fn(request, instrument, run_id)
            return HttpResponse(status=401)
        except:  # noqa: E722
            logging.error("[%s]: %s" % (request.path, sys.exc_info()[1]))
            return HttpResponse(status=500)

    return request_processor


def get_or_create_run(
    instrument,
    run_id,
    expiration_date: datetime = None,
    create: bool = True,
):
    """
    Retrieve a run entry, or create it.
    @param instrument: instrument name
    @param run_id: run number
    @param create: if True, missing entries will be created
    """

    # Get or create the instrument
    instrument_list = Instrument.objects.filter(name=instrument.lower())
    if len(instrument_list) > 0:
        instrument_obj = instrument_list[0]
    elif create:
        instrument_obj = Instrument()
        instrument_obj.name = instrument.lower()
        instrument_obj.save()
    else:
        return None

    # Get or create the run item
    run_list = DataRun.objects.filter(instrument=instrument_obj, run_number=run_id)
    if len(run_list) > 0:
        run_obj = run_list[0]
    elif create:
        run_obj = DataRun()
        run_obj.instrument = instrument_obj
        run_obj.run_number = run_id
        run_obj.expiration_date = expiration_date
        run_obj.save()
    else:
        return None

    return run_obj


def get_plot_data(instrument, run_id, data_type=None):
    """
    Get plot data for requested instrument and run number
    @param instrument: instrument name
    @param run_id: run number
    """
    run_obj = get_or_create_run(instrument, run_id, create=False)
    plot_data_list = PlotData.objects.filter(data_run=run_obj)
    for plot in plot_data_list:
        if data_type is not None:
            if plot.is_data_type_valid(data_type):
                return plot
        else:
            return plot
    return None


def store_user_data(user, data_id, data, data_type, expiration_date: Optional[datetime] = None):
    """
    Store plot data and associate it to a user identifier
    (a name, not an actual user since users don't log in to this system).
    """
    # Get or create the instrument
    instrument_list = Instrument.objects.filter(name=user.lower())
    if len(instrument_list) > 0:
        instrument_obj = instrument_list[0]
    else:
        instrument_obj = Instrument()
        instrument_obj.name = user.lower()
        instrument_obj.save()

    run_list = DataRun.objects.filter(instrument=instrument_obj, run_id=data_id)
    if len(run_list) > 0:
        run_obj = run_list.latest("created_on")
    else:
        run_obj = DataRun()
        run_obj.instrument = instrument_obj
        run_obj.run_number = 0
        run_obj.run_id = data_id
        run_obj.expiration_date = expiration_date
        # Save run object to generate id (primary key)
        run_obj.save()
        # User data has no run number, use the unique id as the run number
        # so that the user can retrieve the data like normal instrument data
        run_obj.run_number = run_obj.id
        run_obj.save()

    # Look for a data file and treat it differently
    data_entries = PlotData.objects.filter(data_run=run_obj)
    if len(data_entries) > 0:
        plot_data = data_entries[0]
    else:
        # No entry was found, create one
        plot_data = PlotData()
        plot_data.data_run = run_obj

    plot_data.data = data
    plot_data.data_type = data_type
    plot_data.timestamp = timezone.now()
    plot_data.save()


def store_plot_data(instrument, run_id, data, data_type, expiration_date: Optional[datetime] = None):
    """
    Store plot data
    @param instrument: instrument name
    @param run_id: run number
    @param data: data to be stored
    @param data_type: requested data type
    """
    run_object = get_or_create_run(instrument, run_id, expiration_date)

    # Look for a data file and treat it differently
    data_entries = PlotData.objects.filter(data_run=run_object)
    if len(data_entries) > 0:
        plot_data = data_entries[0]
    else:
        # No entry was found, create one
        plot_data = PlotData()
        plot_data.data_run = run_object
        plot_data.timestamp = timezone.now()

    plot_data.data = data
    plot_data.data_type = data_type
    plot_data.timestamp = timezone.now()
    plot_data.save()
