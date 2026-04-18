from django.contrib import admin
from .models import Restaurant

admin.site.register(Restaurant)

from .models import Report

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'reported_by', 'created_at', 'is_resolved')
    list_filter = ('is_resolved', 'created_at')
    search_fields = ('restaurant__name', 'reason')