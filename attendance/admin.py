from django.contrib import admin
from .models import Attendance, Course 

# Hoca ders saatlerini ve 30 dk ayarını buradan yapacak
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_time', 'is_active')
    filter_horizontal = ('students',) 

class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'date', 'time_in')
    list_filter = ('date', 'course')

admin.site.register(Course, CourseAdmin)
admin.site.register(Attendance, AttendanceAdmin)