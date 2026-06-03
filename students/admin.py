from django.contrib import admin
from .models import Student

# Admin panelinin en üstündeki başlıkları genel bir yoklama sistemine çevirelim
admin.site.site_header = "Yoklama Sistemi Yönetimi"
admin.site.site_title = "Sistem Yöneticisi"
admin.site.index_title = "Yönetim Paneline Hoş Geldiniz"

class StudentAdmin(admin.ModelAdmin):
    # Sınıf bilgisi Esma'nın güncellediği kısımdan gelene kadar 
    # geçici olarak departmanı 'Sınıf' gibi gösteriyoruz.
    list_display = ('student_id', 'first_name', 'last_name', 'sinif_goster')
    search_fields = ('first_name', 'last_name', 'student_id')

    # Bu küçük ayar sayesinde veritabanında departman yazsa bile 
    # hoca panelde 'Sınıf' başlığını görecek.
    def sinif_goster(self, obj):
        return obj.department
    sinif_goster.short_description = 'Sınıf'

admin.site.register(Student, StudentAdmin)