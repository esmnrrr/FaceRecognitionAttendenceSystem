from django.db import models
from students.models import Student


class Course(models.Model):
    name = models.CharField(max_length=100, verbose_name="Course Name")
    start_time = models.TimeField(verbose_name="Course Start Time")
    is_active = models.BooleanField(default=True, verbose_name="Active")

    def __str__(self):
        return f"{self.name} ({self.start_time})"

    class Meta:
        verbose_name = "Course"
        verbose_name_plural = "Course Settings"


class Attendance(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        verbose_name="Student"
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Course"
    )

    date = models.DateField(
        auto_now_add=True,
        verbose_name="Date"
    )

    time_in = models.TimeField(
        verbose_name="Check In Time"
    )

    def __str__(self):
        return f"{self.student.first_name} - {self.date}"

    class Meta:
        verbose_name = "Attendance Record"
        verbose_name_plural = "Attendance Records"