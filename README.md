# 🎓 Face Recognition Attendance System

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-27338e?style=for-the-badge&logo=OpenCV&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)

A smart, automated, and highly optimized attendance tracking system built with Django and OpenCV. This system uses facial recognition to automatically detect students and log their attendance during scheduled class hours, eliminating the need for manual roll calls.

## ✨ Key Features

* **🧠 Smart Sleep Mode & CPU Optimization:** The camera goes into "Standby Mode" (black screen) when no active courses are scheduled, drastically reducing CPU/RAM usage.
* **🔄 Dynamic Course Auto-Switching:** The system automatically checks the weekly schedule and activates the correct course. It listens for a 30-minute window starting from the course's scheduled time.
* **🛡️ Anti-Spam Cooldown System:** Implemented a 30-second cooldown per student to prevent database spamming if a student stands in front of the camera for a long time.
* **📊 Dynamic Dashboard & Live Stats:** The web interface dynamically updates to show real-time attendance statistics (Present/Absent) specifically filtered for the currently active course.
* **🗄️ Single Source of Truth Database Architecture:** Optimized Many-To-Many and ForeignKey relationships between Students, Courses, and Attendance records to prevent data conflicts (e.g., `CASCADE` and `SET_NULL` implementations).
* **🇬🇧 Fully Localized:** 100% English UI and Admin Panel for a professional user experience.

## 🛠️ Tech Stack

* **Backend:** Python 3.11, Django 5
* **Computer Vision:** OpenCV, `face_recognition`, NumPy
* **Database:** SQLite (Development)
* **Frontend:** HTML, CSS, JavaScript

## 🚀 How to Run the Project

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/FaceRecognitionAttendenceSystem.git](https://github.com/esmnrrr/FaceRecognitionAttendenceSystem)
    cd FaceRecognitionAttendenceSystem
    ```

2.  **Activate your virtual environment:**
    ```bash
    # Windows
    .\venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: You might need to install C++ Build Tools for the `dlib` and `face_recognition` libraries to compile successfully).*

4.  **Run database migrations:**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

5.  **Create a superuser (for Admin Panel access):**
    ```bash
    python manage.py createsuperuser
    ```

6.  **Start the server:**
    ```bash
    python manage.py runserver
    ```

7.  **Usage:** * Go to `http://127.0.0.1:8000/admin` to add Courses and Students (make sure to upload clear profile photos).
    * Go to `http://127.0.0.1:8000/` to open the live camera feed and start tracking!

## 👥 Team 

* **Esmanur Tetik** - *Developer*
* **Gözde Alan** - *Developer*
* **Zeliha Amine Çelikkök** - *Developer*