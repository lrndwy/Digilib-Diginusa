import os

from django.contrib import messages
from django.contrib.auth import (authenticate, login, logout,
                                 update_session_auth_hash)
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import GuruForm, SiswaForm
from .models import *


def index(request):
    semua_buku = Buku.objects.filter(untuk=None, status=True)
    context = {
        'semua_buku': semua_buku
    }
    return render(request, 'page/landing_page.html', context)


# Auth
def login_siswa_dan_guru(request):
    if request.user.is_authenticated:
        try:
            siswa = Siswa.objects.get(user=request.user)
            return redirect('dashboard')
        except Siswa.DoesNotExist:
            try:
                guru = Guru.objects.get(user=request.user)
                return redirect('dashboard_guru')
            except Guru.DoesNotExist:
                messages.error(request, 'Akun ini bukan akun siswa atau guru.')
                logout(request)
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            try:
                siswa = Siswa.objects.get(user=user)
                return redirect('dashboard')
            except Siswa.DoesNotExist:
                try:
                    guru = Guru.objects.get(user=user)
                    return redirect('dashboard_guru')
                except Guru.DoesNotExist:
                    messages.error(request, 'Akun ini bukan akun siswa atau guru.')
                    logout(request)
        else:
            messages.error(request, 'Username atau password salah.')
    
    return render(request, 'page/login.html')

def logout_user(request):
    logout(request)
    return redirect('login_siswa_dan_guru')


# Render
@login_required
def render_buku(request, buku_id):
    buku = get_object_or_404(Buku, id=buku_id)
    file_extension = os.path.splitext(buku.file_buku.name)[1].lower()
    
    context = {
        'buku': buku,
        'file_type': 'pdf' if file_extension == '.pdf' else 'docx'
    }
    return render(request, 'render/buku.html', context)

@login_required
def flippdf_render(request, flipbook_id):
    flippdf = get_object_or_404(FlipPDF, id=flipbook_id)
    return render(request, 'render/flippdf.html', {'flippdf': flippdf})

@login_required
def render_materi(request, materi_id):
    materi = get_object_or_404(MateriGuru, id=materi_id)
    context = {
        'materi': materi
    }
    return render(request, 'render/materi.html', context)

# Guru
def is_guru(user):
    return hasattr(user, 'guru')

def guru_required(view_func):
    decorated_view_func = login_required(login_url='login_siswa_dan_guru')(user_passes_test(is_guru, login_url='login_siswa_dan_guru')(view_func))
    return decorated_view_func

@guru_required
def dashboard_guru(request):
    try:
        guru = Guru.objects.get(user=request.user)
        materi_guru = MateriGuru.objects.filter(guru=guru, sekolah=guru.sekolah)
        perangkat_kurikulum = PerangkatKurikulum.objects.filter(guru=guru, sekolah=guru.sekolah)
        
        buku_all = Buku.objects.filter(Q(untuk=None) | Q(untuk=guru.sekolah), status=True)
        flippdf_all = FlipPDF.objects.filter(Q(untuk=None) | Q(untuk=guru.sekolah), status=True)
        mata_pelajaran = MataPelajaran.objects.all()
        
        kelas = request.GET.get('kelas')
        mapel = request.GET.get('mapel')
        
        if kelas:
            buku_all = buku_all.filter(kelas=kelas)
            flippdf_all = flippdf_all.filter(kelas=kelas)
        
        if mapel:
            buku_all = buku_all.filter(mata_pelajaran__id=mapel)
            flippdf_all = flippdf_all.filter(mata_pelajaran__id=mapel)
        
        kelas_choices = [(k.id, k.nama_jenjang_kelas) for k in JenjangDanKelas.objects.all()]
        
        context = {
            'guru': guru,
            'materi_guru': materi_guru,
            'perangkat_kurikulum': perangkat_kurikulum,
            'buku_all': buku_all,
            'flippdf_all': flippdf_all,
            'mata_pelajaran': mata_pelajaran,
            'kelas_choices': kelas_choices,
        }
        return render(request, 'guru/dashboard.html', context)
    except Guru.DoesNotExist:
        logout(request)
        return redirect('login_siswa_dan_guru')

@guru_required
def tentang_akun_guru(request):
    guru = Guru.objects.get(user=request.user)
    if request.method == 'POST':
        form = GuruForm(request.POST, instance=guru)
        password_form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Informasi akun berhasil diperbarui.')
            
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Kata sandi berhasil diubah.')
            
            return redirect('tentang_akun_guru')
    else:
        form = GuruForm(instance=guru)
        password_form = PasswordChangeForm(request.user)
    
    context = {
        'form': form,
        'password_form': password_form,
        'guru': guru,
    }
    return render(request, 'guru/tentang_akun.html', context)

@guru_required
def crud_buku(request):
    guru = request.user.guru
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create':
            buku = Buku(
                nama_buku=request.POST['nama_buku'],
                file_buku=request.FILES['file_buku'],
                penerbit=request.POST['penerbit'],
                kelas_id=request.POST['kelas'],
                mata_pelajaran=guru.mata_pelajaran,
                status=request.POST.get('status') == 'on',
                untuk=guru.sekolah
            )
            buku.save()
            messages.success(request, 'Buku berhasil ditambahkan.')
        elif action == 'update':
            buku = get_object_or_404(Buku, id=request.POST['id'], untuk=guru.sekolah)
            buku.nama_buku = request.POST['nama_buku']
            if 'file_buku' in request.FILES:
                buku.file_buku = request.FILES['file_buku']
            buku.penerbit = request.POST['penerbit']
            buku.kelas_id = request.POST['kelas']
            buku.status = request.POST.get('status') == 'on'
            buku.save()
            messages.success(request, 'Buku berhasil diperbarui.')
        elif action == 'delete':
            buku = get_object_or_404(Buku, id=request.POST['id'], untuk=guru.sekolah)
            buku.delete()
            messages.success(request, 'Buku berhasil dihapus.')
        return redirect('crud_buku')
    
    buku_list = Buku.objects.filter(untuk=guru.sekolah, mata_pelajaran=guru.mata_pelajaran)
    kelas_list = JenjangDanKelas.objects.all()
    mata_pelajaran_list = MataPelajaran.objects.all()
    context = {
        'guru': guru,
        'buku_list': buku_list,
        'kelas_list': kelas_list,
        'mata_pelajaran_list': mata_pelajaran_list,
    }
    return render(request, 'guru/crud_buku.html', context)

@guru_required
def crud_materi(request):
    guru = request.user.guru
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create':
            materi = MateriGuru(
                nama_materi=request.POST['nama_materi'],
                file_materi=request.FILES['file_materi'],
                mata_pelajaran_id=guru.mata_pelajaran.id,
                guru=guru,
                sekolah=guru.sekolah,
                kelas_id=request.POST['kelas'],
                status=request.POST.get('status') == 'on'
            )
            materi.save()
            messages.success(request, 'Materi berhasil ditambahkan.')
        elif action == 'update':
            materi = get_object_or_404(MateriGuru, id=request.POST['id'], guru=guru)
            materi.nama_materi = request.POST['nama_materi']
            if 'file_materi' in request.FILES:
                materi.file_materi = request.FILES['file_materi']
            materi.kelas_id = request.POST['kelas']
            materi.status = request.POST.get('status') == 'on'
            materi.save()
            messages.success(request, 'Materi berhasil diperbarui.')
        elif action == 'delete':
            materi = get_object_or_404(MateriGuru, id=request.POST['id'], guru=guru)
            materi.delete()
            messages.success(request, 'Materi berhasil dihapus.')
        return redirect('crud_materi')
    
    
    materi_list = MateriGuru.objects.filter(guru=guru, mata_pelajaran_id=guru.mata_pelajaran.id)
    kelas_list = JenjangDanKelas.objects.all()
    mata_pelajaran_list = MataPelajaran.objects.all()
    context = {
        'guru': guru,
        'materi_list': materi_list,
        'kelas_list': kelas_list,
        'mata_pelajaran_list': mata_pelajaran_list,
    }
    return render(request, 'guru/crud_materi.html', context)

@guru_required
def crud_perangkat_kurikulum(request):
    guru = request.user.guru
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create':
            perangkat = PerangkatKurikulum(
                nama_pk=request.POST['nama_pk'],
                file_pk=request.FILES['file_pk'],
                mata_pelajaran_id=guru.mata_pelajaran.id,
                guru=guru,
                sekolah=guru.sekolah
            )
            perangkat.save()
            messages.success(request, 'Perangkat Kurikulum berhasil ditambahkan.')
        elif action == 'update':
            perangkat = get_object_or_404(PerangkatKurikulum, id=request.POST['id'], guru=guru)
            perangkat.nama_pk = request.POST['nama_pk']
            if 'file_pk' in request.FILES:
                perangkat.file_pk = request.FILES['file_pk']
            perangkat.mata_pelajaran_id = guru.mata_pelajaran.id
            perangkat.save()
            messages.success(request, 'Perangkat Kurikulum berhasil diperbarui.')
        elif action == 'delete':
            perangkat = get_object_or_404(PerangkatKurikulum, id=request.POST['id'], guru=guru)
            perangkat.delete()
            messages.success(request, 'Perangkat Kurikulum berhasil dihapus.')
        return redirect('crud_perangkat_kurikulum')
    
    perangkat_list = PerangkatKurikulum.objects.filter(guru=guru, mata_pelajaran_id=guru.mata_pelajaran.id)
    mata_pelajaran_list = MataPelajaran.objects.all()
    context = {
        'guru': guru,
        'perangkat_list': perangkat_list,
        'mata_pelajaran_list': mata_pelajaran_list,
    }
    return render(request, 'guru/crud_perangkat_kurikulum.html', context)

@guru_required
def crud_flippdf(request):
    guru = request.user.guru
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create':
            flippdf = FlipPDF(
                title=request.POST['title'],
                kelas_id=request.POST['kelas'],
                mata_pelajaran_id=guru.mata_pelajaran.id,
                zip_file=request.FILES['zip_file'],
                status=request.POST.get('status') == 'on',
                untuk=guru.sekolah
            )
            flippdf.save()
            messages.success(request, 'FlipPDF berhasil ditambahkan.')
        elif action == 'update':
            flippdf = get_object_or_404(FlipPDF, id=request.POST['id'], untuk=guru.sekolah)
            flippdf.title = request.POST['title']
            flippdf.kelas_id = request.POST['kelas']
            if 'zip_file' in request.FILES:
                flippdf.zip_file = request.FILES['zip_file']
            flippdf.status = request.POST.get('status') == 'on'
            flippdf.save()
            messages.success(request, 'FlipPDF berhasil diperbarui.')
        elif action == 'delete':
            flippdf = get_object_or_404(FlipPDF, id=request.POST['id'], untuk=guru.sekolah)
            flippdf.delete()
            messages.success(request, 'FlipPDF berhasil dihapus.')
        return redirect('crud_flippdf')

    flippdf_list = FlipPDF.objects.filter(untuk=guru.sekolah, mata_pelajaran_id=guru.mata_pelajaran.id)
    kelas_list = JenjangDanKelas.objects.all()
    mata_pelajaran_list = MataPelajaran.objects.all()
    context = {
        'guru': guru,
        'flippdf_list': flippdf_list,
        'kelas_list': kelas_list,
        'mata_pelajaran_list': mata_pelajaran_list,
    }
    return render(request, 'guru/crud_flippdf.html', context)

# Siswa
def is_siswa(user):
    return hasattr(user, 'siswa')

def siswa_required(view_func):
    decorated_view_func = login_required(login_url='login_siswa_dan_guru')(user_passes_test(is_siswa, login_url='login_siswa_dan_guru')(view_func))
    return decorated_view_func

@siswa_required
def dashboard(request):
    try:
        siswa = Siswa.objects.select_related('sekolah').get(user=request.user)
        mata_pelajaran = MataPelajaran.objects.filter()
        
        selected_mapel = request.GET.get('mapel')
        if selected_mapel:
            buku_kelas = Buku.objects.filter(
                kelas=siswa.kelas, 
                mata_pelajaran__id=selected_mapel, 
                status=True
            ).filter(untuk__isnull=True) | Buku.objects.filter(
                kelas=siswa.kelas, 
                mata_pelajaran__id=selected_mapel, 
                status=True, 
                untuk=siswa.sekolah
            )
            flippdf_kelas = FlipPDF.objects.filter(
                kelas=siswa.kelas,
                mata_pelajaran__id=selected_mapel,
                status=True
            ).filter(untuk__isnull=True) | FlipPDF.objects.filter(
                kelas=siswa.kelas,
                mata_pelajaran__id=selected_mapel,
                status=True,
                untuk=siswa.sekolah
            )
        else:
            buku_kelas = Buku.objects.filter(
                kelas=siswa.kelas, 
                status=True
            ).filter(untuk__isnull=True) | Buku.objects.filter(
                kelas=siswa.kelas, 
                status=True, 
                untuk=siswa.sekolah
            )
            flippdf_kelas = FlipPDF.objects.filter(
                kelas=siswa.kelas,
                status=True
            ).filter(untuk__isnull=True) | FlipPDF.objects.filter(
                kelas=siswa.kelas,
                status=True,
                untuk=siswa.sekolah
            )
        
        materi_guru = MateriGuru.objects.filter(kelas=siswa.kelas, sekolah=siswa.sekolah)
        if selected_mapel:
            materi_guru = materi_guru.filter(mata_pelajaran__id=selected_mapel, status=True)
    
    except Siswa.DoesNotExist:
        siswa = None
        buku_kelas = []
        mata_pelajaran = []
        selected_mapel = None
        materi_guru = []
        flippdf_kelas = []

    context = {
        'siswa': siswa,
        'buku_kelas': buku_kelas,
        'mata_pelajaran': mata_pelajaran,
        'selected_mapel': selected_mapel,
        'materi_guru': materi_guru,
        'flippdf_kelas': flippdf_kelas,
    }
    return render(request, 'siswa/dashboard.html', context)

@siswa_required
def tentang_akun(request):
    siswa = Siswa.objects.get(user=request.user)
    if request.method == 'POST':
        form = SiswaForm(request.POST, instance=siswa)
        password_form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Informasi akun berhasil diperbarui.')
            
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password berhasil diubah.')
            
            return redirect('tentang_akun')
    else:
        form = SiswaForm(instance=siswa)
        password_form = PasswordChangeForm(request.user)
    
    context = {
        'form': form,
        'password_form': password_form,
        'siswa': siswa
    }
    return render(request, 'siswa/tentang_akun.html', context)


def custom_404(request, exception):
    return render(request, 'page/404.html', status=404)

def custom_500(request):
    return render(request, 'page/500.html', status=500)


