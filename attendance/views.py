from django.shortcuts import render
from django.http import StreamingHttpResponse
import cv2
import face_recognition
import numpy as np
from students.models import Student
from attendance.models import Attendance, Course
from django.utils import timezone
from datetime import datetime, timedelta

# =====================================================================
# KAMERA VE YÜZ TANIMA MOTORU (CORE ENGINE)
# =====================================================================
class VideoCamera(object):
    def __init__(self):
        # 1. Kamerayı başlat (0: Varsayılan bilgisayar kamerası)
        self.video = cv2.VideoCapture(0)

        if not self.video.isOpened():
            print("Camera could not be opened.")

        # Tüm okulu değil, sadece o dersteki öğrencileri RAM'e alıyoruz (Performans Optimizasyonu)
        self.known_face_encodings = []
        self.known_face_ids = []
        self.known_face_names = []
        
        # Spam engelleme için öğrencilerin son görülme zamanlarını tutan sözlük
        self.last_seen = {}

        print("\n--- SYSTEM STARTING: LOADING TODAY'S FACES ---")
        
        # 2. Bugün haftanın hangi günü olduğunu bul (0=Pazartesi, 6=Pazar)
        bugunun_gunu = timezone.localtime(timezone.now()).date().weekday()
        
        # 3. Veritabanından sadece "Aktif" ve "Bugün olan" dersleri getir
        aktif_dersler = Course.objects.filter(is_active=True, day_of_week=bugunun_gunu)
        
        if not aktif_dersler:
            print("Warning: No active courses found for TODAY!")
            
        # 4. Bugün dersi olan tüm öğrencilerin fotoğraflarını 128 boyutlu vektörlere (encoding) çevir
        for ders in aktif_dersler:
            print(f"Today's Course Found: {ders.name} | Registered Students: {ders.students.count()}")
            students = ders.students.all()
            
            for student in students:
                # Aynı öğrenci iki farklı dersteyse RAM'e iki kere yüklememek için kontrol
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
                            
                    except Exception as e: 
                        print(f"❌ FILE ERROR ({student.first_name}): {e}")
                        
        print(f"--- LOADING COMPLETE: {len(self.known_face_encodings)} faces ready ---\n")

    def __del__(self):
        # Sınıf kapatıldığında kamerayı serbest bırak (Memory Leak engelleme)
        if self.video.isOpened():
            self.video.release()

    # =====================================================================
    # GÖRÜNTÜ İŞLEME VE AKILLI UYKU MODU (FRAME PROCESSING)
    # =====================================================================
    def get_frame(self):
        bugunun_tarihi = timezone.localtime(timezone.now()).date()
        su_an = timezone.localtime(timezone.now()).time()
        bugunun_gunu = bugunun_tarihi.weekday()
        
        ders_zamani_mi = False
        su_anki_ders = None
        
        # 1. OTOMATİK DERS GEÇİŞİ (Auto-Switch)
        aktif_dersler = Course.objects.filter(is_active=True, day_of_week=bugunun_gunu)
        for ders in aktif_dersler:
            baslangic = ders.start_time
            tam_tarih = datetime.combine(bugunun_tarihi, baslangic)
            # Ders başlangıcından itibaren 30 dakika boyunca sistemi açık tutuyoruz
            bitis_zamani = (tam_tarih + timedelta(minutes=30)).time()
            
            if baslangic <= su_an <= bitis_zamani:
                ders_zamani_mi = True
                su_anki_ders = ders
                break 
        
        # 2. AKILLI UYKU MODU
        if not ders_zamani_mi:
            black_image = np.zeros((480, 640, 3), dtype=np.uint8)
            mesaj = "System on Standby (Waiting for Course...)" if aktif_dersler else "No Active Courses Set for Today."
            cv2.putText(black_image, mesaj, (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            ret, jpeg = cv2.imencode('.jpg', black_image)
            if not ret:
                return None
            return jpeg.tobytes()

        # 3. YÜZ TANIMA İŞLEMİ
        success, image = self.video.read()
        if not success:
            print("Frame could not be read.")
            return None

        # İşlemci hızını artırmak için görüntüyü 1/4 oranında küçült
        small_frame = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Küçültülmüş karede yüzlerin yerini ve vektörlerini (encodings) bul
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []

        for face_encoding in face_encodings:
            name = "Unknown"
            student_id = None

            if len(self.known_face_encodings) > 0:
                # Kameradaki yüzü, RAM'deki yüzlerle karşılaştır (Tolerance: 0.6)
                matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)

                if len(face_distances) > 0:
                    best_match_index = np.argmin(face_distances) # En çok benzeyen yüzü bul

                    if matches[best_match_index]:
                        name = self.known_face_names[best_match_index]
                        student_id = self.known_face_ids[best_match_index]
                        current_time = timezone.localtime(timezone.now())

                        # 4. ANTI-SPAM SİSTEMİ (30 Saniye Cooldown)
                        # Öğrenci kameraya her baktığında veritabanını yormamak için süre kontrolü
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

        # 5. EKRANA ÇİZİM YAP (Kare ve İsim)
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Koordinatları tekrar orijinal boyuta (x4) döndür
            top *= 4; right *= 4; bottom *= 4; left *= 4
            
            # Tanınan kişiye yeşil, tanınmayana kırmızı kutu
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)

            cv2.rectangle(image, (left, top), (right, bottom), color, 2)
            cv2.rectangle(image, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            cv2.putText(image, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

        # Görüntüyü web için JPEG formatına dönüştür
        ret, jpeg = cv2.imencode('.jpg', image)
        if not ret:
            return None
        return jpeg.tobytes()

    # =====================================================================
    # VERİTABANI KAYIT SİSTEMİ (DATABASE RECORDING)
    # =====================================================================
    def record_attendance(self, student_id, su_anki_ders):
        today = timezone.localtime(timezone.now()).date()
        now = timezone.localtime(timezone.now()).time()
        student = Student.objects.get(id=student_id)

        # get_or_create kullanarak aynı öğrencinin aynı derse çift kayıt atmasını engelliyoruz
        obj, created = Attendance.objects.get_or_create(
            student=student,
            course=su_anki_ders,
            date=today
        )

        # Eğer kayıt ilk defa oluşturuluyorsa (created == True), giriş saatini işle
        if created:
            obj.time_in = now
            obj.save()
            print(f"✅ Attendance recorded: {student.first_name} {student.last_name}")

# =====================================================================
# WEB ARAYÜZÜ (FRONTEND DASHBOARD & STATISTICS)
# =====================================================================
def index(request):
    today = timezone.localtime(timezone.now()).date()
    su_an = timezone.localtime(timezone.now()).time()
    bugunun_gunu = today.weekday()
    
    # 1. Hangi dersin aktif olduğunu ve arayüz butonlarının yeşil yanıp yanmayacağını belirle
    tum_aktif_dersler = Course.objects.filter(is_active=True, day_of_week=bugunun_gunu)
    gercek_aktif_ders = None
    is_system_active = False # HTML'deki durum butonlarını (System Status) kontrol eder

    for ders in tum_aktif_dersler:
        baslangic = ders.start_time
        # Şu anki saat, dersin başlangıcı ile 30 dk sonrası arasında mı?
        if baslangic <= su_an <= (datetime.combine(today, baslangic) + timedelta(minutes=30)).time():
            gercek_aktif_ders = ders
            is_system_active = True
            break

    # 2. Ders varsa ilgili kayıtları çek, ders bittiyse (uyku modunda) tabloyu temizle
    if gercek_aktif_ders:
        attendance_list = Attendance.objects.filter(
            date=today,
            course=gercek_aktif_ders
        ).order_by('-time_in')
        
        total_students = gercek_aktif_ders.students.count() 
    else:
        attendance_list = Attendance.objects.none()
        total_students = 0

    # 3. İstatistiksel Hesaplamalar
    present_count = attendance_list.count()
    absent_count = total_students - present_count
    last_attendance = attendance_list.first()

    # 4. Verileri HTML sayfasına gönder (Context)
    return render(request, 'attendance/index.html', {
        'attendance_list': attendance_list,     # Yoklama tablosu verileri
        'total_students': total_students,       # O derse kayıtlı toplam öğrenci
        'present_count': present_count,         # Gelenler (Yeşil rozet)
        'absent_count': absent_count,           # Gelmeyenler (Kırmızı rozet)
        'last_attendance': last_attendance,     # Son okutulan kişi
        'active_course': gercek_aktif_ders,     # Ekranda yazacak dersin adı
        'is_system_active': is_system_active,   # Uyku modunda mı aktif mi?
    })

# =====================================================================
# KAMERA YAYIN (STREAMING) FONKSİYONLARI
# =====================================================================
def gen(camera):
    # Kameradan gelen kareleri (frame) sürekli olarak (yield) web sayfasına iter
    while True:
        frame = camera.get_frame()
        if frame:
            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n'
            )

def video_feed(request):
    # gen() fonksiyonundan gelen görüntü parçalarını HTTP yanıtı olarak tarayıcıya (HTML'e) yansıtır
    return StreamingHttpResponse(
        gen(VideoCamera()),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )