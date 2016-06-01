from django.contrib import admin
from plots.models import DataRun, Instrument, PlotData

class PlotDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'data_run', 'data_type', 'timestamp')

admin.site.register(DataRun)
admin.site.register(Instrument)
admin.site.register(PlotData, PlotDataAdmin)