from django.contrib import admin
from plots.models import DataRun, Instrument, PlotData

class PlotDataAdmin(admin.ModelAdmin):
    readonly_fields=('data_run',)
    list_display = ('id', 'data_run', 'data_type', 'timestamp')

admin.site.register(DataRun)
admin.site.register(Instrument)
admin.site.register(PlotData, PlotDataAdmin)