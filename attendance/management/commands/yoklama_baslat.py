from django.core.management.base import BaseCommand
import cv2
import face_recognition
from employees.models import Student
from attendance.models import Attendance, Course
from django.utils import timezone
import numpy as np
import time
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Yüz tanıma tabanlı yoklama sistemini zaman ayarlı olarak başlatır'

    def handle(self, *args, **kwargs):
        self.stdout.write("Sistem uyku modunda. Ders saati bekleniyor...")

        while True:
            # 1. Veritabanından hocanın aktif ettiği dersi al
            bugunun_tarihi = timezone.localtime(timezone.now()).date()
            aktif_ders = Course.objects.filter(is_active=True).first()

            ders_zamani_mi = False
            bitis_zamani = None

            # Eğer bugün için bir ders tanımlanmışsa saatini kontrol et
            if aktif_ders:
                su_an = timezone.localtime(timezone.now()).time()
                baslangic = aktif_ders.start_time
                
                # Bitiş saatini 30 dakika sonrası olarak hesapla
                tam_tarih = datetime.combine(bugunun_tarihi, baslangic)
                bitis_zamani = (tam_tarih + timedelta(minutes=30)).time()

                # Şu anki saat, başlangıç ve bitiş arasındaysa kamerayı açma izni ver
                if baslangic <= su_an <= bitis_zamani:
                    ders_zamani_mi = True
            
            # --- KAMERANIN ÇALIŞACAĞI AKTİF BÖLGE ---
            if ders_zamani_mi:
                self.stdout.write(self.style.SUCCESS(f"Ders saati geldi! Kamera açılıyor... (Kapanış: {bitis_zamani})"))
                
                # Veritabanından Kullanıcıları Yükle (Sadece ders başlarken yükler)
                known_face_encodings = []
                known_face_ids = []
                known_face_names = []

                # Sadece o an aktif olan dersin öğrencilerini filtrele
                students = aktif_ders.students.all()
                for student in students:
                    try:
                        image_path = student.photo.path
                        person_image = face_recognition.load_image_file(image_path)
                        encodings = face_recognition.face_encodings(person_image)

                        if len(encodings) > 0:
                            encoding = encodings[0]
                            known_face_encodings.append(encoding)
                            known_face_ids.append(student.id)
                            known_face_names.append(f"{student.first_name} {student.last_name}")
                            self.stdout.write(self.style.SUCCESS(f"Yüklendi: {student.first_name} {student.last_name}"))
                        else:
                            self.stdout.write(self.style.ERROR(f"Yüz bulunamadı: {student.first_name}"))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Hata ({student.first_name}): {e}"))

                # Kamerayı Başlat
                video_capture = cv2.VideoCapture(0)
                self.stdout.write("Yoklama başladı. Erken çıkmak için 'q' tuşuna basın.")
                last_seen = {}

                while True:
                    # OTOMATİK KAPANMA KONTROLÜ (30 DAKİKA DOLDU MU?)
                    if timezone.localtime(timezone.now()).time() > bitis_zamani:
                        self.stdout.write(self.style.WARNING("Yoklama süresi (30 dk) doldu. Kamera otomatik kapatılıyor."))
                        break # İç döngüyü kırar, kamerayı kapatır.

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
                                
                                # Kişiyi kaydet
                                if person_id not in last_seen:
                                    self.record_attendance(person_id, name)
                                    last_seen[person_id] = current_time
                                elif (current_time - last_seen[person_id]).seconds > 30:
                                    # Sadece son görülmeyi günceller, spam yapmasını engeller
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

                    cv2.imshow('Yuz Tanima Yoklama Sistemi', frame)

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

                # Süre dolunca veya q'ya basınca kamerayı serbest bırak
                video_capture.release()
                cv2.destroyAllWindows()
                
                # Kamera kapandıktan sonra arka arkaya tekrar açılmasın diye biraz bekletiyoruz
                time.sleep(10)
            
            # --- DERS SAATİ DEĞİLSE BEKLEME BÖLGESİ ---
            else:
                # Sistemi yormamak için 10 saniyede bir saati kontrol eder
                time.sleep(10)

    def record_attendance(self, person_id, name):
        """Kişi tespit edildiğinde veritabanına SADECE GİRİŞ kaydeder."""
        today = timezone.now().date()
        now_time = timezone.now().time()
        
        student = Student.objects.get(id=person_id)
        existing_record = Attendance.objects.filter(student=student, date=today).first()

        if not existing_record:
            # Sadece o gün ilk defa görülüyorsa kayıt yapar
            Attendance.objects.create(student=student, date=today, time_in=now_time)
            self.stdout.write(self.style.SUCCESS(f"✅ GİRİŞ YAPILDI: {name} - {now_time.strftime('%H:%M:%S')}"))