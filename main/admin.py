from django.contrib import admin
from .models import *

# === KONFIGURASI TAMPILAN ADMIN ===

@admin.register(ProfilPengguna)
class ProfilPenggunaAdmin(admin.ModelAdmin):
    list_display = ('user', 'peran', 'poin', 'no_hp')
    list_filter = ('peran',)
    search_fields = ('user__username', 'no_hp')

@admin.register(AreaLingkungan)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('nama_jalan', 'rt_rw')
    search_fields = ('nama_jalan',)

@admin.register(AlamatWarga)
class AlamatAdmin(admin.ModelAdmin):
    list_display = ('user', 'label', 'area', 'detail_lain')
    search_fields = ('user__username', 'area__nama_jalan')
    list_filter = ('area',)

@admin.register(PermintaanJemput)
class RequestAdmin(admin.ModelAdmin):
    # MENAMPILKAN KOLOM UTAMA DI TABEL
    list_display = (
        'pemohon', 
        'jenis_sampah',     # Baru: Biar admin tau sampahnya apa
        'alamat', 
        'kurir_pemeriksa', 
        'status', 
        'tanggal_jemput'    # Baru: Sesuai request kamu
    )
    
    # FILTER SAMPING (MEMUDAHKAN PENCARIAN)
    list_filter = ('status', 'jenis_sampah', 'tanggal_jemput')
    
    # KOLOM PENCARIAN
    search_fields = ('pemohon__username', 'catatan')
    
    # AGAR LEBIH RAPI: Urutkan dari request terbaru
    ordering = ('-tanggal_jemput',)

@admin.register(Transaksi)
class TransaksiAdmin(admin.ModelAdmin):
    list_display = ('user', 'jumlah', 'tipe', 'keterangan', 'tanggal')
    list_filter = ('tipe', 'tanggal')

@admin.register(Berita)
class BeritaAdmin(admin.ModelAdmin):
    list_display = ('judul', 'tanggal_upload')
    search_fields = ('judul',)

@admin.register(Jadwal)
class JadwalAdmin(admin.ModelAdmin):
    list_display = ('kurir', 'area_target', 'hari_tanggal', 'keterangan')
    list_filter = ('hari_tanggal',)