from django.db import models
from employees.models import Student 

class Course(models.Model):
    name = models.CharField(max_length=100, verbose_name="Ders Adı")
    start_time = models.TimeField(verbose_name="Ders Başlangıç Saati")
    is_active = models.BooleanField(default=True, verbose_name="Sistem Açık mı?")
    students = models.ManyToManyField('employees.Student', related_name='courses', blank=True)

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

    def __str__(self):
        return f"{self.student.first_name} - {self.date}"

    class Meta:
        verbose_name = "Yoklama Kaydı"
        verbose_name_plural = "Yoklama Kayıtları"