from django.db import models
from employees.models import Employee # Personel tablosunu buraya bağlıyoruz

class Attendance(models.Model):
    # Hangi çalışan? (Employee tablosuna bağlantı - ForeignKey)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    
    # Hangi tarih? (Sadece tarih: 2023-10-27)
    date = models.DateField(auto_now_add=True)
    
    # Saat kaçta girdi? (Sadece saat: 09:00:15)
    time_in = models.TimeField(auto_now_add=True)
    
    # Çıkış saati (İsteğe bağlı, başta boş olabilir)
    time_out = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.employee.first_name} - {self.date} {self.time_in}"