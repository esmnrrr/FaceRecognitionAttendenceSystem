from django.shortcuts import render
from django.http import StreamingHttpResponse
import cv2
import face_recognition
import numpy as np
from students.models import Student
from attendance.models import Attendance, Course
from django.utils import timezone
from datetime import datetime, timedelta

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)

        if not self.video.isOpened():
            print("Camera could not be opened.")

        self.known_face_encodings = []
        self.known_face_ids = []
        self.known_face_names = []
        self.last_seen = {}

        # --- SENİN AKILLI VE DEDEKTİF DÖNGÜN ---
        print("\n--- SYSTEM STARTING: LOADING FACES ---")
        aktif_dersler = Course.objects.filter(is_active=True)
        
        if not aktif_dersler:
            print("Warning: No active courses found right now!")
            
        for ders in aktif_dersler:
            print(f"Active Course Found: {ders.name} | Registered Students: {ders.students.count()}")
            students = ders.students.all()
            
            for student in students:
                if student.id not in self.known_face_ids:
                    try:
                        img = face_recognition.load_image_file(student.photo.path)
                        encodings = face_recognition.face_encodings(img)

                        if len(encodings) > 0:
                            enc = encodings[0]
                            self.known_face_encodings.append(enc)
                            self.known_face_ids.append(student.id)
                            self.known_face_names.append(f"{student.first_name} {student.last_name}")
                            print(f"✅ SUCCESS: {student.first_name} loaded into memory!")
                        else:
                            print(f"❌ ERROR: No face found in {student.first_name}'s photo!")
                            
                    except Exception as e: # Arkadaşının eklediği hata yakalama
                        print(f"❌ FILE ERROR ({student.first_name}): {e}")
                        
        print(f"--- LOADING COMPLETE: {len(self.known_face_encodings)} faces ready ---\n")

    def __del__(self):
        if self.video.isOpened():
            self.video.release()

    def get_frame(self):
        bugunun_tarihi = timezone.localtime(timezone.now()).date()
        su_an = timezone.localtime(timezone.now()).time()
        
        ders_zamani_mi = False
        su_anki_ders = None
        
        # HANGİ DERSİN SAATİNDEYİZ ONU BUL
        aktif_dersler = Course.objects.filter(is_active=True)
        for ders in aktif_dersler:
            baslangic = ders.start_time
            tam_tarih = datetime.combine(bugunun_tarihi, baslangic)
            bitis_zamani = (tam_tarih + timedelta(minutes=30)).time()
            
            if baslangic <= su_an <= bitis_zamani:
                ders_zamani_mi = True
                su_anki_ders = ders
                break 
        
        # EĞER DERS ZAMANI DEĞİLSE SİYAH EKRAN (SENİN ÖZELLİĞİN)
        if not ders_zamani_mi:
            black_image = np.zeros((480, 640, 3), dtype=np.uint8)
            mesaj = "System on Standby (Waiting for Course...)" if aktif_dersler else "No Active Courses Set."
            cv2.putText(black_image, mesaj, (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            ret, jpeg = cv2.imencode('.jpg', black_image)
            if not ret:
                return None
            return jpeg.tobytes()

        # DERS ZAMANIYSA YÜZ TANIMA İŞLEMİ
        success, image = self.video.read()

        if not success:
            print("Frame could not be read.")
            return None

        small_frame = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []

        for face_encoding in face_encodings:
            name = "Unknown"
            student_id = None

            if len(self.known_face_encodings) > 0:
                matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)

                if len(face_distances) > 0:
                    best_match_index = np.argmin(face_distances)

                    if matches[best_match_index]:
                        name = self.known_face_names[best_match_index]
                        student_id = self.known_face_ids[best_match_index]

                        current_time = timezone.localtime(timezone.now())

                        # ARKADAŞININ EKLEDİĞİ GÜVENLİ (TRY-EXCEPT) KAYIT SİSTEMİ
                        if student_id not in self.last_seen:
                            try:
                                self.record_attendance(student_id, su_anki_ders)
                                self.last_seen[student_id] = current_time
                            except Exception as e:
                                print(f"Attendance recording error: {e}")

                        elif (current_time - self.last_seen[student_id]).seconds > 30:
                            try:
                                self.record_attendance(student_id, su_anki_ders)
                                self.last_seen[student_id] = current_time
                            except Exception as e:
                                print(f"Attendance recording error: {e}")

            face_names.append(name)

        for (top, right, bottom, left), name in zip(face_locations, face_names):
            top *= 4; right *= 4; bottom *= 4; left *= 4
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)

            cv2.rectangle(image, (left, top), (right, bottom), color, 2)
            cv2.rectangle(image, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            cv2.putText(image, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

        ret, jpeg = cv2.imencode('.jpg', image)
        if not ret:
            return None
        return jpeg.tobytes()

    def record_attendance(self, student_id, su_anki_ders):
        today = timezone.localtime(timezone.now()).date()
        now = timezone.localtime(timezone.now()).time()

        student = Student.objects.get(id=student_id)

        # GET_OR_CREATE mantığı: Eğer bugün bu öğrenci bu derse zaten geldiyse, tekrar oluşturma
        obj, created = Attendance.objects.get_or_create(
            student=student,
            course=su_anki_ders,
            date=today
        )

        # Eğer kayıt yeni oluşturulduysa saati işle
        if created:
            obj.time_in = now
            obj.save()
            print(f"✅ Attendance recorded: {student.first_name} {student.last_name}")

# --- SENİN İSTATİSTİKLİ VE DİNAMİK ARAYÜZ KODLARIN ---
def index(request):
    today = timezone.localtime(timezone.now()).date()
    su_an = timezone.localtime(timezone.now()).time()
    
    # Şu an aktif bir ders var mı?
    tum_aktif_dersler = Course.objects.filter(is_active=True)
    gercek_aktif_ders = None
    is_system_active = False # <-- HTML'i yeşil yapacak sihirli değişken geri geldi!

    for ders in tum_aktif_dersler:
        # Basit bir saat kontrolü: (Başlangıç < Su_an < Başlangıç + 30 dk)
        baslangic = ders.start_time
        if baslangic <= su_an <= (datetime.combine(today, baslangic) + timedelta(minutes=30)).time():
            gercek_aktif_ders = ders
            is_system_active = True # <-- Dersin saati geldiyse sistemi aktif (True) yap
            break

    # EĞER DERS VARSA SADECE O DERSE AİT KAYITLARI ÇEK
    if gercek_aktif_ders:
        attendance_list = Attendance.objects.filter(
            date=today,
            course=gercek_aktif_ders
        ).order_by('-time_in')
        
        # İstatistikler için toplam öğrenci sayısı
        total_students = gercek_aktif_ders.students.count() 
    else:
        # Ders yoksa tabloyu tamamen boşalt
        attendance_list = Attendance.objects.none()
        total_students = 0

    # UI (Arayüz) İstatistikleri
    present_count = attendance_list.count()
    absent_count = total_students - present_count
    last_attendance = attendance_list.first()

    return render(request, 'attendance/index.html', {
        'attendance_list': attendance_list,
        'total_students': total_students,       # <-- Geri eklendi
        'present_count': present_count,         # <-- Geri eklendi
        'absent_count': absent_count,           # <-- Geri eklendi
        'last_attendance': last_attendance,     # <-- Geri eklendi
        'active_course': gercek_aktif_ders,
        'is_system_active': is_system_active,   # <-- Geri eklendi (BUTONLAR YEŞİL OLACAK)
    })

def gen(camera):
    while True:
        frame = camera.get_frame()
        if frame:
            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n'
            )

def video_feed(request):
    return StreamingHttpResponse(
        gen(VideoCamera()),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )