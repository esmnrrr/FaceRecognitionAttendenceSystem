from django.shortcuts import render
from django.http import StreamingHttpResponse
import cv2
import face_recognition
import numpy as np
from employees.models import Employee
from attendance.models import Attendance
from django.utils import timezone

# Kamera Sınıfı
class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        
        # Veritabanındaki yüzleri hafızaya al
        self.known_face_encodings = []
        self.known_face_ids = []
        self.known_face_names = []
        
        employees = Employee.objects.all()
        for emp in employees:
            try:
                img = face_recognition.load_image_file(emp.photo.path)
                enc = face_recognition.face_encodings(img)[0]
                self.known_face_encodings.append(enc)
                self.known_face_ids.append(emp.id)
                self.known_face_names.append(f"{emp.first_name} {emp.last_name}")
            except:
                pass

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, image = self.video.read()
        if not success:
            return None
            
        # Resmi küçült ve işle
        small_frame = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "Bilinmiyor"
            
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]
                    emp_id = self.known_face_ids[best_match_index]
                    # Yoklamayı kaydet
                    self.record_attendance(emp_id)
            
            face_names.append(name)

        # Kutuları çiz
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            top *= 4; right *= 4; bottom *= 4; left *= 4
            cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.rectangle(image, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
            cv2.putText(image, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

    def record_attendance(self, person_id):
        today = timezone.now().date()
        now = timezone.now().time()
        emp = Employee.objects.get(id=person_id)
        
        # Giriş yoksa oluştur, varsa çıkışı güncelle
        obj, created = Attendance.objects.get_or_create(employee=emp, date=today)
        if created:
            obj.time_in = now
            obj.save()
        else:
            obj.time_out = now
            obj.save()

# Görünümler
def index(request):
    attendance_list = Attendance.objects.filter(date=timezone.now().date()).order_by('-time_in')
    return render(request, 'attendance/index.html', {'attendance_list': attendance_list})

def gen(camera):
    while True:
        frame = camera.get_frame()
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def video_feed(request):
    return StreamingHttpResponse(gen(VideoCamera()),
                                 content_type='multipart/x-mixed-replace; boundary=frame')