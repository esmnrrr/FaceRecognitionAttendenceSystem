from django.contrib import admin
from .models import Attendance, Course # Yeni eklediğimiz Course tablosunu çağırdık

# Hoca ders saatlerini ve 30 dk ayarını buradan yapacak
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_time', 'is_active')
    filter_horizontal = ('students',) 

class AttendanceAdmin(admin.ModelAdmin):
    # time_out (çıkış saati) yok, sadece giriş var
    list_display = ('student', 'course', 'date', 'time_in')
    list_filter = ('date', 'course')

admin.site.register(Course, CourseAdmin)
admin.site.register(Attendance, AttendanceAdmin)