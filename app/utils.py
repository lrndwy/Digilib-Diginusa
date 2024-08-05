import openpyxl
from django.contrib.auth.models import User
from .models import *

def process_excel_file_siswa(excel_file):
    try:
        workbook = openpyxl.load_workbook(excel_file)
        worksheet = workbook.active
        
        for row_num, row in enumerate(worksheet.iter_rows(min_row=2, values_only=True), start=2):
            if len(row) < 7:  # Pastikan baris memiliki cukup kolom
                continue
            
            _, nama, username, password, email, nama_sekolah, kelas = row
            
            # Pastikan username tidak kosong dan unik
            if not username:
                continue  # Lewati baris dengan username kosong
            
            # Cek apakah username sudah ada
            if User.objects.filter(username=username).exists():
                continue  # Lewati username yang sudah ada
            
            try:
                sekolah = Sekolah.objects.get(nama=nama_sekolah)
            except Sekolah.DoesNotExist:
                continue  # Lewati jika sekolah tidak ditemukan
            
            try:
                kelas_obj = JenjangDanKelas.objects.get(nama_jenjang_kelas=kelas)
            except JenjangDanKelas.DoesNotExist:
                continue  # Lewati jika kelas tidak ditemukan
            
            user = User.objects.create_user(username=username, email=email, password=password)
            Siswa.objects.create(
                user=user,
                nama=nama,
                sekolah=sekolah,
                kelas=kelas_obj
            )
        
        return {'success': True, 'message': 'Data siswa berhasil diimpor'}
    except Exception as e:
        return {'success': False, 'error': str(e)}
    
    

def process_excel_file_guru(excel_file):
    try:
        workbook = openpyxl.load_workbook(excel_file)
        worksheet = workbook.active
        
        for row_num, row in enumerate(worksheet.iter_rows(min_row=2, values_only=True), start=2):
            if len(row) < 7:  # Pastikan baris memiliki cukup kolom
                continue
            
            # Ambil 7 nilai pertama dari baris
            _, nama, username, password, email, nama_sekolah, nama_mata_pelajaran = row[:7]
            
            # Pastikan username tidak kosong dan unik
            if not username:
                continue  # Lewati baris dengan username kosong
            
            # Cek apakah username sudah ada
            if User.objects.filter(username=username).exists():
                continue  # Lewati username yang sudah ada
            
            try:
                sekolah = Sekolah.objects.get(nama=nama_sekolah)
                mata_pelajaran = MataPelajaran.objects.get(mata_pelajaran=nama_mata_pelajaran)
            except (Sekolah.DoesNotExist, MataPelajaran.DoesNotExist):
                continue  # Lewati jika sekolah atau mata pelajaran tidak ditemukan
            
            user = User.objects.create_user(username=username, email=email, password=password)
            Guru.objects.create(
                user=user,
                nama=nama,
                sekolah=sekolah,
                mata_pelajaran=mata_pelajaran
            )
        
        return {'success': True, 'message': 'Data guru berhasil diimpor'}
    except Exception as e:
        return {'success': False, 'error': str(e)}