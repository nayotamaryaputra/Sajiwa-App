from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from main import views  # Pastikan 'main' sesuai nama aplikasi Anda
from django.conf import settings             # 1. Import pengaturan
from django.conf.urls.static import static   # 2. Import fungsi static

urlpatterns = [
    # === 1. ADMIN BAWAAN DJANGO ===
    path('admin/', admin.site.urls),

    # === 2. AUTHENTICATION (Login & Logout) ===
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # === 3. MENU UTAMA ===
    path('', views.beranda, name='beranda'),
    path('berita/', views.halaman_berita, name='berita'),
    path('jemput/', views.halaman_jemput, name='jemput'),
    path('riwayat/', views.halaman_riwayat, name='riwayat'),
    path('pengguna/', views.pengguna, name='pengguna'),

    # === 4. AKSI KHUSUS ===
    path('ambil-tugas/<int:id_jemput>/', views.ambil_tugas, name='ambil_tugas'),
    path('selesaikan-tugas/<int:id_jemput>/', views.selesaikan_tugas, name='selesaikan_tugas'),
]

# === BAGIAN PENTING: KONFIGURASI GAMBAR ===
# Kode ini memberitahu Django cara menampilkan gambar di mode development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)