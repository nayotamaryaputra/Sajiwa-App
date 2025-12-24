from django import forms
from django.contrib.auth.models import User
from .models import *

# === CUSTOM WIDGETS (DARK GLASS STYLE) ===
# Widget ini membungkus class Tailwind agar kita tidak perlu mengetik ulang di setiap field

class DarkInput(forms.TextInput):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs.update({
            'class': 'w-full p-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-400 focus:outline-none focus:border-green-500 focus:ring-1 focus:ring-green-500 transition duration-200'
        })

class DarkEmail(forms.EmailInput):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs.update({
            'class': 'w-full p-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-400 focus:outline-none focus:border-green-500 focus:ring-1 focus:ring-green-500 transition duration-200'
        })

class DarkPassword(forms.PasswordInput):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs.update({
            'class': 'w-full p-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-400 focus:outline-none focus:border-green-500 focus:ring-1 focus:ring-green-500 transition duration-200'
        })

class DarkSelect(forms.Select):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs.update({
            'class': 'w-full p-3 rounded-xl bg-white/5 border border-white/10 text-white focus:outline-none focus:border-green-500 focus:ring-1 focus:ring-green-500 transition duration-200 [&>option]:bg-gray-900 [&>option]:text-white'
        })

class DarkTextarea(forms.Textarea):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs.update({
            'class': 'w-full p-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-400 focus:outline-none focus:border-green-500 focus:ring-1 focus:ring-green-500 transition duration-200',
            'rows': 3
        })

class DarkNumber(forms.NumberInput):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs.update({
            'class': 'w-full p-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-400 focus:outline-none focus:border-green-500 focus:ring-1 focus:ring-green-500 transition duration-200'
        })


# === 1. ADMIN FORMS ===

class FormBuatAkun(forms.Form):
    username = forms.CharField(widget=DarkInput(attrs={'placeholder': 'Username'}))
    email = forms.EmailField(widget=DarkEmail(attrs={'placeholder': 'Alamat Email'}))
    no_hp = forms.CharField(widget=DarkInput(attrs={'placeholder': 'Nomor Handphone'}), required=False)
    password = forms.CharField(widget=DarkPassword(attrs={'placeholder': 'Password'}))
    peran = forms.ChoiceField(
        choices=[('warga', 'Warga'), ('kurir', 'Kurir')], 
        widget=DarkSelect()
    )

class FormArea(forms.ModelForm):
    class Meta:
        model = AreaLingkungan
        fields = ['nama_jalan', 'rt_rw']
        widgets = {
            'nama_jalan': DarkInput(attrs={'placeholder': 'Nama Jalan / Blok'}),
            'rt_rw': DarkInput(attrs={'placeholder': 'RT 00 / RW 00'}),
        }

class FormBayar(forms.Form):
    TARGET_CHOICES = [('warga', 'Semua Warga'), ('kurir', 'Semua Kurir')]
    target = forms.ChoiceField(choices=TARGET_CHOICES, widget=DarkSelect())
    total_dana = forms.DecimalField(widget=DarkNumber(attrs={'placeholder': 'Total Dana (Rp)'}))
    keterangan = forms.CharField(widget=DarkInput(attrs={'placeholder': 'Keterangan (Gaji/Bonus)'}))

class FormAssignTugas(forms.Form):
    # Admin memilih Warga, Alamat Warga, dan Kurir untuk membuat tugas manual
    warga = forms.ModelChoiceField(
        queryset=User.objects.filter(profilpengguna__peran='warga'), 
        widget=DarkSelect(), 
        empty_label="Pilih Warga"
    )
    alamat = forms.ModelChoiceField(
        queryset=AlamatWarga.objects.all(), 
        widget=DarkSelect(), 
        empty_label="Pilih Alamat Target"
    )
    kurir = forms.ModelChoiceField(
        queryset=User.objects.filter(profilpengguna__peran='kurir'), 
        widget=DarkSelect(), 
        empty_label="Tugaskan ke Kurir"
    )


# === 2. WARGA FORMS ===

class FormAlamat(forms.ModelForm):
    class Meta:
        model = AlamatWarga
        fields = ['label', 'area', 'detail_lain']
        widgets = {
            'label': DarkInput(attrs={'placeholder': 'Label (Rumah/Kantor)'}),
            'area': DarkSelect(),
            'detail_lain': DarkTextarea(attrs={'placeholder': 'Detail (Nomor rumah, warna pagar, patokan...)'}),
        }

class FormRequestWarga(forms.ModelForm):
    class Meta:
        model = PermintaanJemput
        fields = ['alamat', 'catatan']
        widgets = {
            'alamat': DarkSelect(),
            'catatan': DarkTextarea(attrs={'placeholder': 'Catatan tambahan untuk kurir...'}),
        }
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter agar Warga hanya bisa memilih alamat miliknya sendiri
        self.fields['alamat'].queryset = AlamatWarga.objects.filter(user=user)
        self.fields['alamat'].empty_label = "Pilih Lokasi Penjemputan"


# === 3. KURIR FORMS ===

class FormLaporanKurir(forms.Form):
    # Form ini hanya muncul saat kurir menyelesaikan tugas
    berat = forms.FloatField(
        widget=forms.NumberInput(attrs={
            'class': 'w-full p-4 text-4xl font-bold text-center text-white bg-transparent border-b-2 border-green-500 focus:outline-none placeholder-gray-600', 
            'placeholder': '0.0'
        }),
        label="Berat Sampah (Kg)"
    )