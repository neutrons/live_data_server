"""
    Plot data models
"""
from __future__ import unicode_literals
import sys
import logging
from django.db import models

class Instrument(models.Model):
    """
        Table of instruments
    """
    name = models.CharField(max_length=128, unique=True)
    run_id_type = models.IntegerField(default=0)

    def __unicode__(self):
        return self.name


class DataRun(models.Model):
    """
        Table of runs
    """
    run_number = models.IntegerField()
    # Optional free-form run identifier
    run_id = models.TextField()

    instrument = models.ForeignKey(Instrument)
    created_on = models.DateTimeField('Timestamp', auto_now_add=True)

    def __unicode__(self):
        return "%s_%d_%s" % (self.instrument, self.run_number, self.run_id)


class PlotData(models.Model):
    """
        Table of plot data. This data can either be json or html
    """
    ## DataRun this run status belongs to
    data_run = models.ForeignKey(DataRun)
    ## Data type:
    ##    type = 100 for live data, 0 static reduced.
    ##    type += 1 for HTML, 0 for JSON
    data_type = models.IntegerField()

    ## JSON/HTML data
    data = models.TextField()

    timestamp = models.DateTimeField('Timestamp')

    def __unicode__(self):
        return "%s" % self.data_run

    def is_div(self):
        """
            Return whether the data is a <div>
        """
        return self.data_type%100 == 1

    def is_data_type_valid(self, data_type):
        """
            Verify that a given data type matches the stored data
            @param data_type: data type to check
        """
        try:
            data_type = int(data_type)
            return self.data_type == data_type%100
        except ValueError:
            logging.getLogger('plots.models').error("Could not verify data type: %s", sys.exc_value)
            return False

    @classmethod
    def get_data_type_from_data(cls, data):
        """
            Inspect the data to guess what type it is.
            @param data: block of text to store
        """
        if data.startswith('<div'):
            return 1
        return 0

