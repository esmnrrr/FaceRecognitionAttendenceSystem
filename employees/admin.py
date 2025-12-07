from django.contrib import admin
from .models import Employee

# Bu kısım panelde nasıl görüneceğini ayarlar
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('emp_id', 'first_name', 'last_name', 'role', 'department')
    search_fields = ('first_name', 'last_name', 'emp_id')

# İşte sihirli satır burası! Bunu yazmazsan panelde görünmez.
admin.site.register(Employee, EmployeeAdmin)