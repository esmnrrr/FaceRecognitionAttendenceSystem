from django.contrib import admin
from .models import Student

# Admin panel titles
admin.site.site_header = "Attendance System Management"
admin.site.site_title = "System Administrator"
admin.site.index_title = "Welcome to the Administration Panel"


class StudentAdmin(admin.ModelAdmin):
    list_display = (
        'student_id',
        'first_name',
        'last_name',
        'department_display'
    )

    search_fields = (
        'first_name',
        'last_name',
        'student_id'
    )

    filter_horizontal = ('courses',)

    def department_display(self, obj):
        return obj.department

    department_display.short_description = 'Department'


admin.site.register(Student, StudentAdmin)