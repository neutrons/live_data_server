"""
    Utility functions to support views.
"""
from plots.models import Instrument, DataRun, PlotData

def get_or_create_run(instrument, run_id, create=True):
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

def store_plot_data(instrument, run_id, data):
    pass
    