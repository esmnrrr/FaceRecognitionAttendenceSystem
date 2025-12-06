import cv2
import face_recognition

def main():
    # -----------------------------------------------------------
    # ADIM 1: Veritabanı Hazırlığı (Tanınacak Kişiler)
    # -----------------------------------------------------------
    print("Yüz veritabanı yükleniyor...")
    
    known_face_encodings = []
    known_face_names = []

    try:
        # ÖRNEK: 1. Kişiyi Yükle
        image_1 = face_recognition.load_image_file("taninan_yuzler/esmanur.jpg")
        encoding_1 = face_recognition.face_encodings(image_1)[0]
        
        known_face_encodings.append(encoding_1)
        known_face_names.append("Esmanur Tetik") # Ekranda görünecek isim
        
        print(f"Toplam {len(known_face_names)} kişi sisteme yüklendi.")

    except IndexError:
        print("HATA: Yüklediğiniz fotoğrafta yüz bulunamadı! Lütfen fotoğrafı kontrol edin.")
        return
    except FileNotFoundError:
        print("HATA: Dosya bulunamadı! 'taninan_yuzler' klasörünü ve dosya ismini kontrol edin.")
        return

    # -----------------------------------------------------------
    # ADIM 2: Kamera Başlatma
    # -----------------------------------------------------------
    video_capture = cv2.VideoCapture(0)
    print("Kamera açılıyor... Çıkmak için 'q' tuşuna basın.")

    while True:
        # Kameradan bir kare oku
        ret, frame = video_capture.read()
        if not ret:
            print("Kameradan görüntü alınamadı.")
            break

        # İşlemleri hızlandırmak için görüntüyü 1/4 oranında küçült
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # BGR (OpenCV) -> RGB (face_recognition) dönüşümü
        # rgb_small_frame = small_frame[:, :, ::-1] # Eski versiyonlarda bu kullanılır
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB) # Daha güvenli yöntem

        # Yüzleri bul
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []

        # Bulunan her yüzü hafızadaki yüzlerle karşılaştır
        for face_encoding in face_encodings:
            # Eşleşme var mı?
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Bilinmiyor"

            # En iyi eşleşmeyi bul (En düşük mesafe en iyi benzerliktir)
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            
            # Eğer en az bir eşleşme varsa
            if len(face_distances) > 0:
                best_match_index = face_distances.argmin() # En küçük mesafenin indexi
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]

            face_names.append(name)

        # -----------------------------------------------------------
        # ADIM 3: Sonuçları Çizme
        # -----------------------------------------------------------
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Koordinatları 4 ile çarpıp eski haline getiriyoruz
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Çerçeve rengi: Biliniyorsa Yeşil, Bilinmiyorsa Kırmızı
            color = (0, 255, 0) if name != "Bilinmiyor" else (0, 0, 255)

            # Yüzü kutu içine al
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

            # İsim etiketi
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.8, (255, 255, 255), 1)

        # Sonucu göster
        cv2.imshow('Yuz Tanima Testi', frame)

        # 'q' tuşu ile çıkış
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()