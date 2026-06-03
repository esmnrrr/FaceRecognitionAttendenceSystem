from django.db import models
from students.models import Student

# =====================================================================
# HAFTALIK ZAMAN ÇİZELGESİ (TIME SCHEDULE CONFIGURATION)
# =====================================================================
# Sistemin "Otomatik Uyanma" mantığı için günleri integer (tam sayı) olarak tutuyoruz. 
# Çünkü Python'un datetime kütüphanesi haftanın günlerini 0 (Pazartesi) ile 6 (Pazar) arasında sayar. 
DAYS_OF_WEEK = (
    (0, 'Monday'),
    (1, 'Tuesday'),
    (2, 'Wednesday'),
    (3, 'Thursday'),
    (4, 'Friday'),
    (5, 'Saturday'),
    (6, 'Sunday'),
)

# =====================================================================
# DERS MODELİ (COURSE CORE MODEL)
# =====================================================================
class Course(models.Model):
    # Dersin Adı
    name = models.CharField(max_length=100, verbose_name="Course Name")
    
    # Otomasyon için dersin günü ve saati
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK, default=0, verbose_name="Day of the Week")
    start_time = models.TimeField(verbose_name="Course Start Time")
    
    # Dersin aktif/pasif durumu (Hoca dilerse sistemi manuel kapatabilir)
    is_active = models.BooleanField(default=True, verbose_name="Active")
    
    # "Single Source of Truth" (Tek Doğruluk Kaynağı) Mimarisi.
    # Öğrenci-Ders ilişkisi (ManyToMany) çift yönlü çakışmaları engellemek adına sadece Course üzerinden yönetilmektedir.
    students = models.ManyToManyField('students.Student', related_name='registered_courses', blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_day_of_week_display()} - {self.start_time})"
    
    class Meta:
        verbose_name = "Course"
        verbose_name_plural = "Course Settings"


# =====================================================================
# YOKLAMA KAYDI MODELİ (ATTENDANCE TRANSACTION MODEL)
# =====================================================================
class Attendance(models.Model):
    # "CASCADE" mantığı -> Eğer bir öğrenci okuldan silinirse (kaydı silinirse), 
    # o öğrencinin geçmişteki tüm yoklama kayıtları da veritabanında yer kaplamaması için otomatik silinir.
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="Student")
    
    # "SET_NULL" mantığı -> Eğer bir ders müfredattan kaldırılır/silinirse, 
    # öğrencilerin geçmişteki yoklama (devamsızlık) hakları yanmasın diye kayıtlar SİLİNMEZ, sadece "Ders" kısmı Null (Boş) kalır.
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, verbose_name="Course")
    
    # Yoklamanın atıldığı tarih (Otomatik olarak o günün tarihini alır)
    date = models.DateField(auto_now_add=True, verbose_name="Date")
    
    # Veritabanı seviyesindeki "NOT NULL" hatalarını engellemek için blank=True, null=True yapılmıştır. 
    # Saat bilgisi views.py içinden kod ile manuel basılır.
    time_in = models.TimeField(verbose_name="Check In Time", blank=True, null=True)

    def __str__(self):
        # Admin panelinde kimin, hangi gün geldiğini yazar
        return f"{self.student.first_name} - {self.date}"

    class Meta:
        # Admin panelindeki isimlendirmeler
        verbose_name = "Attendance Record"
        verbose_name_plural = "Attendance Records"