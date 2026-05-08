from django.contrib import admin
from .models import Student

# Bu kısım panelde nasıl görüneceğini ayarlar
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'first_name', 'last_name', 'major', 'department')
    search_fields = ('first_name', 'last_name', 'student_id')

# İşte sihirli satır burası! Bunu yazmazsan panelde görünmez.
admin.site.register(Student, StudentAdmin)
