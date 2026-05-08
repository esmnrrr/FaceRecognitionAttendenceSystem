from django.contrib import admin
from .models import Attendance

class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'time_in', 'time_out')
    list_filter = ('date',) # Tarihe göre filtreleme özelliği ekler

admin.site.register(Attendance, AttendanceAdmin)
