from django.db import models
# Senin klasör adın şu an 'employees' olduğu için böyle bırakıyoruz kanka
from students.models import Student

class Course(models.Model):
    name = models.CharField(max_length=100, verbose_name="Ders Adı")
    start_time = models.TimeField(verbose_name="Ders Başlangıç Saati")
    # Esma'nın "Sistem 30 dk açık kalacak" kuralı için bu saati referans alacağız
    is_active = models.BooleanField(default=True, verbose_name="Sistem Açık mı?")

    def __str__(self):
        return f"{self.name} ({self.start_time})"

    class Meta:
        verbose_name = "Ders Ayarı"
        verbose_name_plural = "Ders Ayarları"

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="Öğrenci")
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, verbose_name="İlgili Ders")
    date = models.DateField(auto_now_add=True, verbose_name="Tarih")
    time_in = models.TimeField(auto_now_add=True, verbose_name="Giriş Saati")
    
    # Esma'nın isteği: "Çıkış saatleri kaldırılacak" 
    # O yüzden time_out sütununu buraya artık eklemiyoruz.

    def __str__(self):
        return f"{self.student.first_name} - {self.date}"

    class Meta:
        verbose_name = "Yoklama Kaydı"
        verbose_name_plural = "Yoklama Kayıtları"