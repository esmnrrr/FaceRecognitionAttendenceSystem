from django.db import models

# Personel rollerini seçenek olarak tanımlıyoruz
ROLE_CHOICES = [
    ('admin', 'Yönetici'),
    ('employee', 'Çalışan'),
]

class Employee(models.Model):
    first_name = models.CharField(max_length=50, verbose_name="Ad")
    last_name = models.CharField(max_length=50, verbose_name="Soyad")
    # Her çalışanın benzersiz bir ID'si olmalı
    emp_id = models.CharField(max_length=20, unique=True, verbose_name="Personel ID")
    
    # Çalışanın yüzünü tanımamız için fotoğrafını yükleyeceğiz
    # 'profile_images/' klasörüne kaydedilecek
    photo = models.ImageField(upload_to='profile_images/', verbose_name="Profil Fotoğrafı")
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='employee')
    
    # Hangi departmanda çalışıyor?
    department = models.CharField(max_length=50, blank=True, null=True)
    
    # Ne zaman işe başladı? (Otomatik tarih atar)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.emp_id})"