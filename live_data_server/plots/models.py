"""
    Plot data models
"""
from __future__ import unicode_literals
import sys
import logging
from django.db import models


DATA_TYPES = {'json': 0, 'html': 1, 'div': 1}
DATA_TYPE_INFO = {0: {'name': 'json'},
                  1: {'name': 'html'}}

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

    instrument = models.ForeignKey(Instrument, on_delete=models.deletion.CASCADE)
    created_on = models.DateTimeField('Timestamp', auto_now_add=True)

    def __unicode__(self):
        return "%s_%d_%s" % (self.instrument, self.run_number, self.run_id)


class PlotData(models.Model):
    """
        Table of plot data. This data can either be json or html
    """
    ## DataRun this run status belongs to
    data_run = models.ForeignKey(DataRun, on_delete=models.deletion.CASCADE)
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
            return self.data_type == data_type%100 or data_type == -1
        except ValueError:
            logging.error("Could not verify data type: %s", sys.exc_value)
            return False

    @classmethod
    def get_data_type_from_data(cls, data):
        """
            Inspect the data to guess what type it is.
            @param data: block of text to store
        """
        if data.startswith(b'<div'):
            return DATA_TYPES['html']
        return DATA_TYPES['json']

    @classmethod
    def get_data_type_from_string(cls, type_string):
        """
            Returns the correct data type ID for a given string representation
        """
        return DATA_TYPES.get(type_string, DATA_TYPES['json'])

    @classmethod
    def data_type_as_string(cls, data_type):
        """
            Return an internal name to use for a given data_type.
            This name is generally used in function names and relates
            to the data format (json or html). In principle, different
            data types can return the same string.

            @param data_type: data type ID [integer]
        """
        data_type = int(data_type)
        data_type_info = DATA_TYPE_INFO.get(data_type)
        if data_type_info is not None:
            return data_type_info['name']
        return None
