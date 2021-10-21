from django.contrib import admin

from .models import User, DfType, pIndicator, Data, Dashboard

# Register your models here.
class pIndicatorAdmin(admin.ModelAdmin):
    list_display = ("id","formula","name","valueType")

class DfTypeAdmin(admin.ModelAdmin):
    list_display = ("id","code","name")

class DashboardAdmin(admin.ModelAdmin):
    list_display = ("user", "index", "data", "type", "market")

class DataAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'dfCode', 'value', 'country')

admin.site.register(pIndicator, pIndicatorAdmin)
admin.site.register(DfType, DfTypeAdmin)
admin.site.register(Dashboard, DashboardAdmin)
admin.site.register(Data, DataAdmin)