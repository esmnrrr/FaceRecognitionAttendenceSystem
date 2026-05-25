from django.core.management.base import BaseCommand
import cv2
import face_recognition
from students.models import Student
from attendance.models import Attendance
from django.utils import timezone
import numpy as np

class Command(BaseCommand):
    help = 'Yüz tanıma tabanlı yoklama sistemini başlatır'

    def handle(self, *args, **kwargs):
        # 1. VERİTABANINDAN KULLANICILARI YÜKLE
        self.stdout.write("Veritabanındaki öğrenciler yükleniyor...")
        
        known_face_encodings = []
        known_face_ids = [] # İsim yerine ID tutacağız, veritabanından çekeceğiz
        known_face_names = []

        students = Student.objects.all()

        for student in students:
            try:
                # Veritabanındaki resim yolunu al
                image_path = student.photo.path
                
                # Resmi yükle ve encode et
                person_image = face_recognition.load_image_file(image_path)
                encodings = face_recognition.face_encodings(person_image)

                if len(encodings) >0:
                    encoding = encodings[0]
                else:
                    self.stdout.write(
                        self.style.ERROR(f"Yüz bulunmadı : {student.first_name}")
                    )
                    continue
                
                known_face_encodings.append(encoding)
                known_face_ids.append(student.id)
                known_face_names.append(f"{student.first_name} {student.last_name}")
                
                self.stdout.write(self.style.SUCCESS(f"Yüklendi: {student.first_name} {student.last_name}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Hata ({student.first_name}): {e}"))

        self.stdout.write(f"Toplam {len(known_face_encodings)} öğrenci hafızaya alındı.")

        # 2. KAMERAYI BAŞLAT
        video_capture = cv2.VideoCapture(0)
        self.stdout.write("Kamera başlatıldı. Çıkmak için 'q' tuşuna basın.")

        last_seen = {}

        while True:
            ret, frame = video_capture.read()
            if not ret:
                break

            # Hızlandırma (1/4 oranında küçültme)
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []

            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Bilinmiyor"
                person_id = None

                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                
                if len(face_distances) > 0:
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = known_face_names[best_match_index]
                        person_id = known_face_ids[best_match_index]

                        current_time = timezone.now()
                        
                        # --- YOKLAMA KAYDI İŞLEMİ BURADA YAPILIYOR ---
                        # kişiyi ilk defa görürse 
                        if person_id not in last_seen:
                            self.record_attendance(person_id, name)
                            last_seen[person_id] = current_time

                        elif (current_time - last_seen[person_id]).seconds > 30:
                            self.record_attendance(person_id, name)
                            last_seen[person_id] = current_time
                        

                face_names.append(name)

            # Ekrana Çizdirme
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                color = (0, 255, 0) if name != "Bilinmiyor" else (0, 0, 255)
                
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

            cv2.imshow('Yüz Tanıma Yoklama Sistemi', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        video_capture.release()
        cv2.destroyAllWindows()

    def record_attendance(self, person_id, name):
        """Kişi tespit edildiğinde veritabanına kaydeder veya günceller"""
        today = timezone.now().date()
        now_time = timezone.now().time()
        
        # Bu kişi için BUGÜN zaten kayıt var mı?
        student = Student.objects.get(id=person_id)
        existing_record = Attendance.objects.filter(student=student, date=today).first()

        if not existing_record:
            # Kayıt yoksa: YENİ GİRİŞ (Check-In)
            Attendance.objects.create(student=student, date=today, time_in=now_time)
            self.stdout.write(self.style.SUCCESS(f"✅ GİRİŞ YAPILDI: {name} - {now_time.strftime('%H:%M:%S')}"))
        else:
            # Kayıt varsa: ÇIKIŞ GÜNCELLE (Check-Out)
            # Sistem seni her gördüğünde çıkış saatini güncelleyecek.
            # Böylece en son görüldüğün an, çıkış saatin olacak.
            existing_record.time_out = now_time
            existing_record.save()
            print(f"🔄 Çıkış Güncellendi: {name} - {now_time.strftime('%H:%M:%S')}")
