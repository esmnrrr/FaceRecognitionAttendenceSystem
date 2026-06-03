# FaceRecognitionAttendenceSystem


#.\venv\Scripts\activate
#python manage.py runserver

#python manage.py yoklama_baslat

#http://127.0.0.1:8000/



# employees/models.py: kimlik gibi bir sey, giris icin bilgileri tutuyoruz, photo = models.ImageField(...) ile aisteme birini kaydederken fotoğrafını yüklüyoruz ve bu fotoğraf profile_images/ klasörüne gidiyor

# attendance/models.py: employee = models.ForeignKey(...): yoklama tablosunu, ogrenci tablosuna bağlıyor yani bu yoklama kaydi bu idli ogrenciye ait diyor

# views.py: 

# __init__: Kamera açılır (cv2.VideoCapture(0)). Sistem her frame'de gidip veritabanından fotoğraf okumak yerine, sistem ilk açıldığında ogrenci tablosundaki tüm ogrencileri döngüye sokup, fotoğraflarını Dlib'in anlayacağı 128 boyutlu yüz vektörlerine (encodings) çevirip RAM'e (self.known_face_encodings) alıyor.

# face_recognition.compare_faces ve face_distance: Ekranda gördüğü yüzü, hafızasındaki yüzlerle karşılaştırır. En küçük mesafe (argmin), en çok benzeyen kişi demektir.

# yuzTanımaTest.py: Bu dosyanın Django sitenle veya veritabanınla doğrudan bir bağlantısı yok! Test icin yazilan kutuphaneler calisiyor mu diye test ettigimiz dosya

# yoklamabaslat.py: small_frame = cv2.resize(...): optimizasyon icin kameradan gelen 1080p veya 720p görüntüyü, yüz aramak için 1/4 oranına küçültüyoruz. Amac gercek zamanli islem yaparken sistemi yormamak. 

# face_distance ve np.argmin: O an kamerada gördüğü yüz vektörü ile Ramdeki yüz vektörleri arasındaki Öklid mesafesini ölçer. Mesafe ne kadar küçükse, yüzler o kadar benziyordur. argmin ile en küçük mesafeyi, yani "en çok benzeyen kişiyi" bulur.

# StreamingHttpResponse: Sürekli olarak bir görüntü (frame) bekler. Eğer ders bittiğinde kamerayı tamamen kapatırsak, web sitesi "Yayın koptu, hata var!" diyerek çöker veya sayfayı dondurur. Siyah ekran göndermek, web sitesine "Yayın bağlantımız sapasağlam duruyor ama şu an sana gösterecek bir dersimiz yok" demenin en güvenli, en profesyonel ve en sisteme dost yoludur. o yzdn sistemi kapatmayip bu sekilde yapiyoruz/ Ayrica sistemi yoran kamera degil, saniyede 30 defa o görüntüyü alıp HOG algoritmasıyla pikselleri analiz etmek, 128 boyutlu vektörler çıkarmak ve veritabanında arama yapmaktır. 