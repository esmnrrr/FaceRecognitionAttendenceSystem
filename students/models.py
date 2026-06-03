from django.db import models

# User role choices
ROLE_CHOICES = [
    ('admin', 'Admin'),
    ('student', 'Student'),
]


class Student(models.Model):
    first_name = models.CharField(
        max_length=50,
        verbose_name="First Name"
    )

    last_name = models.CharField(
        max_length=50,
        verbose_name="Last Name"
    )

    # Unique student number
    student_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Student ID"
    )

    # Student photo used for face recognition
    photo = models.ImageField(
        upload_to='profile_images/',
        verbose_name="Profile Photo"
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='student',
        verbose_name="Role"
    )

    # Department or class information
    department = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Department"
    )

    # Date when the student record was created
    date_created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created Date"
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.student_id})"