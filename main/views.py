from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Sum  # <--- WAJIB DITAMBAH
from django.contrib import messages
from django.db.models import Q
from .models import *
from .forms import *

# === 1. BERANDA (DASHBOARD & ADMIN PANEL) ===
# Tidak pakai @login_required agar tamu bisa lihat preview berita
def beranda(request):
    context = {}
    
    # Data Global: Preview Berita (3 Terbaru)
    context['berita_preview'] = Berita.objects.all().order_by('-tanggal_upload')[:3]

    if request.user.is_authenticated:
        try:
            peran = request.user.profilpengguna.peran
            
            # LOGIC KHUSUS ADMIN
            if peran == 'admin_sajiwa':
                context['form_akun'] = FormBuatAkun()
                context['form_area'] = FormArea()
                context['form_bayar'] = FormBayar()
                
                if request.method == 'POST':
                    # A. Tambah Akun Baru
                    if 'submit_akun' in request.POST:
                        form = FormBuatAkun(request.POST)
                        if form.is_valid():
                            # Buat User Django
                            u = User.objects.create_user(
                                username=form.cleaned_data['username'], 
                                password=form.cleaned_data['password'],
                                email=form.cleaned_data['email']
                            )
                            # Buat Profil Tambahan
                            ProfilPengguna.objects.create(
                                user=u, 
                                peran=form.cleaned_data['peran'], 
                                no_hp=form.cleaned_data['no_hp']
                            )
                            messages.success(request, f"Akun {u.username} berhasil dibuat!")
                            return redirect('beranda')

                    # B. Tambah Master Area
                    elif 'submit_area' in request.POST:
                        form = FormArea(request.POST)
                        if form.is_valid():
                            form.save()
                            messages.success(request, "Area baru berhasil disimpan.")
                            return redirect('beranda')

                    # C. Pembayaran Massal (Gaji/Distribusi)
                    elif 'submit_bayar' in request.POST:
                        form = FormBayar(request.POST)
                        if form.is_valid():
                            target = form.cleaned_data['target']
                            total = form.cleaned_data['total_dana']
                            ket = form.cleaned_data['keterangan']
                            
                            # Cari penerima
                            penerima = User.objects.filter(profilpengguna__peran=target)
                            if penerima.exists():
                                nominal_per_orang = total / penerima.count()
                                for u in penerima:
                                    Transaksi.objects.create(
                                        user=u, 
                                        jumlah=nominal_per_orang, 
                                        tipe='masuk', 
                                        keterangan=ket
                                    )
                                messages.success(request, f"Dana didistribusikan ke {penerima.count()} orang.")
                            else:
                                messages.warning(request, "Tidak ada penerima ditemukan.")
                            return redirect('beranda')

        except:
            pass # Handle error jika user login tapi blm punya profil

    return render(request, 'beranda.html', context)


# === 2. HALAMAN PENGGUNA (PROFIL & POIN) ===
# Bisa diakses tanpa login (untuk tombol masuk), tapi detail butuh login
@login_required
def pengguna(request):
    user = request.user
    profil, created = ProfilPengguna.objects.get_or_create(user=user)
    
    # === 1. LOGIC SALDO (UANG RUPIAH) ===
    # Hitung dari tabel Transaksi (Uang Masuk - Uang Keluar)
    total_masuk = Transaksi.objects.filter(user=user, tipe='masuk').aggregate(total=Sum('jumlah'))['total'] or 0
    total_keluar = Transaksi.objects.filter(user=user, tipe='keluar').aggregate(total=Sum('jumlah'))['total'] or 0
    saldo_real = total_masuk - total_keluar

    # Sync ke database profil biar aman
    if profil.poin != saldo_real:
        profil.poin = saldo_real
        profil.save()
        profil.refresh_from_db()

    context = {
        'profil': profil, # profil.poin = SALDO (Uang)
        'user': user,
    }

    # === 2. LOGIC GAMIFIKASI (EXP MURNI) - KHUSUS WARGA ===
    if profil.peran == 'warga':
        # Hitung XP: Jumlah tugas selesai x 10 poin
        jumlah_setor = PermintaanJemput.objects.filter(pemohon=user, status='selesai').count()
        xp_saat_ini = jumlah_setor * 10  # 1x setor = 10 XP
        
        # Kembali ke standar Level 0-300 (Sesuai request awal)
        # LEVEL 1: BRONZE (0 - 50 XP)
        if xp_saat_ini <= 50:
            level = 'Bronze'
            limit_bawah = 0
            limit_atas = 51
            voucher = 2
            bg_card = 'from-orange-700 to-amber-900' 
            text_color = 'text-orange-400'
            icon_medal = 'fa-medal'
            next_level = 'Silver'
            
        # LEVEL 2: SILVER (51 - 150 XP)
        elif xp_saat_ini <= 150:
            level = 'Silver'
            limit_bawah = 51
            limit_atas = 151
            voucher = 4
            bg_card = 'from-slate-600 to-slate-800'
            text_color = 'text-gray-300'
            icon_medal = 'fa-medal'
            next_level = 'Gold'
            
        # LEVEL 3: GOLD (> 150 XP)
        else: 
            level = 'Gold'
            limit_bawah = 151
            limit_atas = 300 # Visual target
            voucher = 8
            bg_card = 'from-yellow-600 to-yellow-800'
            text_color = 'text-yellow-400'
            icon_medal = 'fa-crown'
            next_level = 'Max'

        # Hitung Persentase Progress Bar
        if level != 'Gold':
            jarak = limit_atas - limit_bawah
            progress = xp_saat_ini - limit_bawah
            persen = (progress / jarak) * 100 if jarak > 0 else 0
            sisa = limit_atas - xp_saat_ini
        else:
            persen = 100
            sisa = 0

        context.update({
            'xp_saat_ini': xp_saat_ini, # Kirim variabel XP terpisah
            'level_user': level,
            'voucher_dapat': voucher,
            'persen_progress': int(persen),
            'sisa_ke_next': sisa,
            'bg_card': bg_card,
            'text_color': text_color,
            'icon_medal': icon_medal,
            'next_level_name': next_level,
            'target_poin': limit_atas
        })

    return render(request, 'pengguna.html', context)


# === 3. BERITA (CRUD ADMIN & READ ALL) ===
def halaman_berita(request):
    # --- LOGIKA 1: HAPUS BERITA (Jika ada request hapus) ---
    if request.method == 'POST' and 'hapus_id' in request.POST:
        id_hapus = request.POST.get('hapus_id')
        try:
            berita_hapus = Berita.objects.get(id=id_hapus)
            berita_hapus.delete()
            messages.success(request, "Berita berhasil dihapus.")
        except Berita.DoesNotExist:
            messages.error(request, "Berita tidak ditemukan.")
        return redirect('berita')

    # --- LOGIKA 2: TAMBAH BERITA (Jika ada request tambah) ---
    if request.method == 'POST' and 'tambah_berita' in request.POST:
        judul = request.POST.get('judul')
        isi = request.POST.get('isi')
        gambar = request.FILES.get('gambar') # <-- Ambil data gambar
            
        # Simpan ke database
        Berita.objects.create(judul=judul, isi=isi, gambar=gambar)
        messages.success(request, "Berita berhasil dipublikasikan!")
        return redirect('berita')

    # --- LOGIKA 3: TAMPILKAN BERITA (PENTING!) ---
    # Ambil semua berita, urutkan dari yang terbaru (-)
    semua_berita = Berita.objects.all().order_by('-tanggal_upload')

    context = {
        # Nama 'daftar_berita' ini HARUS SAMA dengan yang di loop HTML: {% for b in daftar_berita %}
        'daftar_berita': semua_berita  
    }

    return render(request, 'berita.html', {'berita': semua_berita})


# === 4. MENU JEMPUT (LOGIKA 3 TAB: ALAMAT, JEMPUT, JADWAL) ===
@login_required
def halaman_jemput(request):
    user = request.user
    # Safety Check Peran
    try: peran = user.profilpengguna.peran
    except: peran = 'warga' 

    context = {}
    context['semua_area'] = AreaLingkungan.objects.all()

    # === LOGIKA POST (AKSI DARI POP-UP) ===
    if request.method == 'POST':
        
        # 1. WARGA: Tambah/Edit Alamat
        if 'simpan_alamat' in request.POST and peran == 'warga':
            id_alamat = request.POST.get('id_alamat') # Kalau ada ID berarti Edit
            area_id = request.POST.get('area_id')
            label = request.POST.get('label_alamat')
            detail = request.POST.get('alamat_lengkap')
            
            area_obj = AreaLingkungan.objects.get(id=area_id)
            
            if id_alamat: # Edit Mode
                alamat = get_object_or_404(AlamatWarga, id=id_alamat, user=user)
                alamat.area = area_obj
                alamat.label = label
                alamat.detail_lain = detail
                alamat.save()
                messages.success(request, "Alamat berhasil diperbarui.")
            else: # Tambah Baru
                AlamatWarga.objects.create(user=user, area=area_obj, label=label, detail_lain=detail)
                messages.success(request, "Alamat baru ditambahkan.")
            return redirect('jemput')

        # 2. WARGA: Request Jemput (Hanya Lapor)
        elif 'request_jemput' in request.POST and peran == 'warga':
            jenis = request.POST.get('jenis_sampah')
            alamat_id = request.POST.get('alamat_id')
            catatan = request.POST.get('catatan')
            
            alamat_obj = get_object_or_404(AlamatWarga, id=alamat_id, user=user)
            
            PermintaanJemput.objects.create(
                pemohon=user,
                alamat=alamat_obj,
                jenis_sampah=jenis,
                catatan=catatan,
                status='menunggu' 
                # Tanggal & Jam kosong dulu
            )
            messages.success(request, "Permintaan terkirim! Admin akan mengatur jadwal.")
            return redirect('jemput')

        # 3. ADMIN: Atur Jadwal & Kurir
        elif 'atur_jadwal' in request.POST and peran == 'admin_sajiwa':
            id_req = request.POST.get('id_jemput')
            id_kurir = request.POST.get('kurir_id')
            tgl = request.POST.get('tanggal_set')
            jam = request.POST.get('waktu_set')
            
            tugas = get_object_or_404(PermintaanJemput, id=id_req)
            tugas.kurir_pemeriksa_id = id_kurir
            tugas.tanggal_jemput = tgl
            tugas.waktu_jemput = jam
            tugas.status = 'dijemput' # Ubah status
            tugas.save()
            messages.success(request, "Jadwal berhasil ditetapkan.")
            return redirect('jemput')

        # 4. KURIR: Selesaikan Tugas
        elif 'lapor_kurir' in request.POST and peran == 'kurir':
            id_req = request.POST.get('id_jemput')
            berat = request.POST.get('berat_aktual')
            
            tugas = get_object_or_404(PermintaanJemput, id=id_req)
            tugas.berat_real = berat
            tugas.status = 'selesai'
            tugas.save()
            
            # --- UPDATE POIN & CATAT TRANSAKSI ---
            try:
                # 1. Tambah Poin Warga (+10 poin per transaksi, atau bisa hitung dr berat)
                poin_dapat = 10 
                warga_profil = tugas.pemohon.profilpengguna
                warga_profil.poin += poin_dapat
                warga_profil.save()
                
                # 2. Bikin Catatan Riwayat Transaksi (PENTING BUAT HALAMAN RIWAYAT)
                Transaksi.objects.create(
                    user=tugas.pemohon,
                    jumlah=poin_dapat,
                    tipe='masuk',
                    keterangan=f"Jual Sampah {tugas.get_jenis_sampah_display()}"
                )
            except Exception as e:
                print(f"Error update poin: {e}")
            
            messages.success(request, "Tugas selesai! Poin warga telah ditambahkan.")
            return redirect('jemput')

    # === LOGIKA GET (DATA TAMPILAN) ===
    
    # Data Alamat (Semua user butuh)
    if peran == 'warga':
        context['daftar_alamat'] = AlamatWarga.objects.filter(user=user)
    else:
        context['daftar_alamat'] = AlamatWarga.objects.select_related('user', 'area').all()

    # Data Penjemputan (Logic filter)
    if peran == 'warga':
        context['data_request'] = PermintaanJemput.objects.filter(pemohon=user).order_by('-created_at')
    elif peran == 'admin_sajiwa':
        context['data_request'] = PermintaanJemput.objects.all().order_by('-created_at')
        context['list_kurir'] = User.objects.filter(profilpengguna__peran='kurir')
    elif peran == 'kurir':
        context['data_request'] = PermintaanJemput.objects.filter(kurir_pemeriksa=user).order_by('tanggal_jemput')

    # Data Jadwal (Semua request yang sudah dijadwalkan)
    context['data_jadwal'] = PermintaanJemput.objects.exclude(status='menunggu').order_by('-tanggal_jemput')

    return render(request, 'jemput.html', context)


# === 5. HALAMAN RIWAYAT ===
@login_required
def halaman_riwayat(request):
    user = request.user
    try: peran = user.profilpengguna.peran
    except: peran = 'warga'
    
    context = {}

    # === 1. DATA PENJEMPUTAN (Sesuai Peran) ===
    if peran == 'warga':
        context['riwayat_jemput'] = PermintaanJemput.objects.filter(pemohon=user).order_by('-created_at')
    elif peran == 'kurir':
        context['riwayat_jemput'] = PermintaanJemput.objects.filter(kurir_pemeriksa=user, status='selesai').order_by('-tanggal_jemput')
    elif peran == 'admin_sajiwa':
        context['riwayat_jemput'] = PermintaanJemput.objects.all().order_by('-created_at')

    # === 2. DATA TRANSAKSI (Sesuai Peran) ===
    if peran == 'admin_sajiwa':
        # Admin melihat SEMUA transaksi (Distribusi dana ke kurir/warga)
        context['riwayat_transaksi'] = Transaksi.objects.all().order_by('-tanggal')
    else:
        # Warga/Kurir hanya melihat transaksi milik mereka
        context['riwayat_transaksi'] = Transaksi.objects.filter(user=user).order_by('-tanggal')

    # === 3. DATA POIN PEROLEHAN (Tab Baru) ===
    if peran == 'admin_sajiwa':
        # Admin melihat daftar Warga dan Poin mereka (Leaderboard)
        context['data_poin_warga'] = ProfilPengguna.objects.filter(peran='warga').order_by('-poin')
    elif peran == 'warga':
        # Warga melihat history penjemputan TAPI khusus yang sudah selesai (untuk hitung poin)
        # Asumsi: 1 Kg = 10 Poin (sesuai logic di view sebelumnya)
        context['data_poin_saya'] = PermintaanJemput.objects.filter(pemohon=user, status='selesai').order_by('-created_at')

    return render(request, 'riwayat.html', context)


# === 6. AKSI KURIR (AMBIL & SELESAI) ===
@login_required
def ambil_tugas(request, id_jemput):
    # Ubah status jadi 'dijemput'
    tugas = get_object_or_404(PermintaanJemput, id=id_jemput)
    # Pastikan yang klik adalah kurir yang ditugaskan
    if request.user == tugas.kurir_pemeriksa:
        tugas.status = 'dijemput'
        tugas.save()
        messages.success(request, "Status: Sedang Menjemput")
    return redirect('jemput')

@login_required
def selesaikan_tugas(request, id_jemput):
    # Kurir input berat -> Status 'selesai' -> Warga dapat poin
    tugas = get_object_or_404(PermintaanJemput, id=id_jemput)
    if request.method == 'POST':
        berat = request.POST.get('berat')
        tugas.berat_real = berat
        tugas.status = 'selesai'
        tugas.save()
        
        # Tambah Poin Warga (FIX 10 Poin per transaksi, sesuai request)
        warga = tugas.pemohon.profilpengguna
        warga.poin += 10 
        warga.save()
        
        messages.success(request, "Tugas Selesai! Poin (+10) masuk ke warga.")
        
    return redirect('jemput')