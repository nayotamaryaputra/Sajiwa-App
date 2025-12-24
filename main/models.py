from django.db import models
from django.contrib.auth.models import User

# === 1. PROFIL PENGGUNA (ROLE & GAMIFIKASI) ===
class ProfilPengguna(models.Model):
    PERAN_CHOICES = [
        ('warga', 'Warga'),
        ('kurir', 'Kurir'),
        ('admin_sajiwa', 'Admin Sajiwa'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    peran = models.CharField(max_length=20, choices=PERAN_CHOICES, default='warga')
    no_hp = models.CharField(max_length=15, blank=True, null=True)
    poin = models.IntegerField(default=0) 
    
    def __str__(self):
        return f"{self.user.username} ({self.get_peran_display()})"

# === 2. MASTER DATA AREA (RT/RW) ===
class AreaLingkungan(models.Model):
    nama_jalan = models.CharField(max_length=100)
    rt_rw = models.CharField(max_length=50) 
    
    def __str__(self):
        return f"{self.nama_jalan} - {self.rt_rw}"

# === 3. ALAMAT SPESIFIK WARGA ===
class AlamatWarga(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alamat_warga')
    area = models.ForeignKey('AreaLingkungan', on_delete=models.SET_NULL, null=True)
    label = models.CharField(max_length=50, default="Rumah") 
    detail_lain = models.TextField()
    
    def __str__(self):
        return f"{self.user.username} - {self.label}"

# === 4. INTI APLIKASI: REQUEST JEMPUT ===
class PermintaanJemput(models.Model):
    STATUS_CHOICES = [
        ('menunggu', 'Menunggu Jadwal'),
        ('dijemput', 'Terjadwal & Proses'),
        ('selesai', 'Selesai'),
    ]
    
    # === REVISI: Tambah Banyak Kategori ===
    JENIS_SAMPAH_CHOICES = [
        ('plastik', 'Plastik (Botol/Gelas)'),
        ('kertas', 'Kertas / Kardus'),
        ('logam', 'Kaleng / Logam'),
        ('kaca', 'Kaca / Beling'), # Baru
        ('elektronik', 'E-Waste / Elektronik'), # Baru
        ('minyak', 'Minyak Jelantah'), # Baru
        ('tekstil', 'Pakaian / Tekstil'), # Baru
        ('campur', 'Campuran / Lainnya'),
    ]
    
    pemohon = models.ForeignKey(User, on_delete=models.CASCADE, related_name='request_jemput')
    alamat = models.ForeignKey('AlamatWarga', on_delete=models.CASCADE)
    jenis_sampah = models.CharField(max_length=20, choices=JENIS_SAMPAH_CHOICES, default='campur')
    catatan = models.TextField(blank=True, null=True)
    
    tanggal_jemput = models.DateField(null=True, blank=True)
    waktu_jemput = models.TimeField(null=True, blank=True) 
    
    kurir_pemeriksa = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    berat_real = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='menunggu')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Req {self.pemohon.username}"

# === 5. JADWAL / KALENDER ===
class Jadwal(models.Model):
    kurir = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'profilpengguna__peran': 'kurir'})
    area_target = models.ForeignKey(AreaLingkungan, on_delete=models.CASCADE)
    hari_tanggal = models.DateTimeField()
    keterangan = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"Jadwal {self.kurir.username} - {self.area_target}"

# === 6. KEUANGAN & HISTORI POIN ===
class Transaksi(models.Model):
    TIPE_CHOICES = [('masuk', 'Uang Masuk'), ('keluar', 'Uang Keluar')]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    jumlah = models.DecimalField(max_digits=15, decimal_places=0) 
    tipe = models.CharField(max_length=10, choices=TIPE_CHOICES, default='masuk')
    keterangan = models.CharField(max_length=100)
    tanggal = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - Rp {self.jumlah}"

# === 7. BERITA / ARTIKEL ===
class Berita(models.Model):
    judul = models.CharField(max_length=200)
    isi = models.TextField()
    tanggal_upload = models.DateTimeField(auto_now_add=True)
    gambar = models.ImageField(upload_to='berita/', null=True, blank=True)
    
    def __str__(self):
        return self.judul