from django.db import models
from django.contrib.auth.models import User
from django.db import transaction
import os
import fitz
from PIL import Image
from io import BytesIO
from django.core.files import File
import zipfile
from django.conf import settings
import shutil
import logging

logger = logging.getLogger(__name__)

# Table Sekolah
class Sekolah(models.Model):
    nama = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='logo_sekolah/', null=True, blank=True)
    
    def __str__(self):
        return self.nama
    
    def delete(self, *args, **kwargs):
        if self.logo:
            if os.path.isfile(self.logo.path):
                os.remove(self.logo.path)
        super().delete(*args, **kwargs)
    
# Table Mata Pelajaran
class MataPelajaran(models.Model):
    id = models.AutoField(primary_key=True)
    mata_pelajaran = models.CharField(max_length=100)
    
    def __str__(self):
        return self.mata_pelajaran
    
# Table Jenjang dan Kelas
class JenjangDanKelas(models.Model):
    id = models.AutoField(primary_key=True)
    nama_jenjang_kelas = models.CharField(max_length=100)

    def __str__(self):
        return self.nama_jenjang_kelas
    
    class Meta:
        verbose_name_plural = "Jenjang dan Kelas"
        ordering = ['nama_jenjang_kelas']
        
# Table Siswa
class Siswa(models.Model):
    id = models.AutoField(primary_key=True)
    nama = models.CharField(max_length=255)
    sekolah = models.ForeignKey(Sekolah, on_delete=models.CASCADE)
    kelas = models.ForeignKey(JenjangDanKelas, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.nama
    
# Table Guru
class Guru(models.Model):
    id = models.AutoField(primary_key=True)
    nama = models.CharField(max_length=100)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sekolah = models.ForeignKey(Sekolah, on_delete=models.CASCADE)
    mata_pelajaran = models.ForeignKey(MataPelajaran, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.nama

# Table Buku
class Buku(models.Model):
    id = models.AutoField(primary_key=True)
    nama_buku = models.CharField(max_length=255)
    file_buku = models.FileField(upload_to='buku')
    penerbit = models.CharField(max_length=255)
    kelas = models.ForeignKey(JenjangDanKelas, on_delete=models.CASCADE)
    mata_pelajaran = models.ForeignKey(MataPelajaran, on_delete=models.CASCADE)
    cover_image = models.ImageField(upload_to='buku_covers', blank=True, null=True, editable=False)
    status = models.BooleanField(choices=[(True, 'Aktif'), (False, 'Tidak Aktif')], default=False)
    untuk = models.ForeignKey(Sekolah, on_delete=models.CASCADE, blank=True, null=True)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            # Simpan model terlebih dahulu
            super().save(*args, **kwargs)
            
            # Buat cover image jika belum ada
            if self.file_buku and not self.cover_image:
                try:
                    cover_image = create_cover_image(self.file_buku.path)
                    self.cover_image.save(f"cover_{self.nama_buku}.jpg", cover_image, save=False)
                    super().save(update_fields=['cover_image'])
                except Exception as e:
                    print(f"Error saat membuat cover: {str(e)}")
    
    def delete(self, *args, **kwargs):
        # Hapus file buku
        if self.file_buku:
            if os.path.isfile(self.file_buku.path):
                os.remove(self.file_buku.path)
        
        # Hapus cover image
        if self.cover_image:
            if os.path.isfile(self.cover_image.path):
                os.remove(self.cover_image.path)
        
        # Panggil method delete asli
        super().delete(*args, **kwargs)
                    
    def __str__(self):
        return self.nama_buku


def create_cover_image(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File tidak ditemukan: {file_path}")

    try:
        pdf_document = fitz.open(file_path)
        first_page = pdf_document[0]
        pix = first_page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        thumb_io = BytesIO()
        img.save(thumb_io, 'JPEG', quality=85)
        thumb_io.seek(0)
        
        return File(thumb_io, name=f"{os.path.splitext(os.path.basename(file_path))[0]}_cover.jpg")
    finally:
        if 'pdf_document' in locals():
            pdf_document.close()

# Table FlipPDF
class FlipPDF(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    kelas = models.ForeignKey(JenjangDanKelas, on_delete=models.CASCADE)
    mata_pelajaran = models.ForeignKey(MataPelajaran, on_delete=models.CASCADE)
    zip_file = models.FileField(upload_to='temp_zip', null=True, blank=True)
    index_file = models.CharField(max_length=255, blank=True, editable=False)
    cover_file = models.CharField(max_length=255, blank=True, editable=False)
    status = models.BooleanField(choices=[(True, 'Aktif'), (False, 'Tidak Aktif')], default=False)
    untuk = models.ForeignKey(Sekolah, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        verbose_name = "FlipPDF"
        verbose_name_plural = "FlipPDF"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        
        if self.zip_file and self.zip_file.name:
            self.extract_zip()
            self.set_index_file()
            self.set_cover_file()
            self.save_without_extraction()

    def save_without_extraction(self):
        super().save(update_fields=['index_file', 'cover_file', 'zip_file'])

    def extract_zip(self):
        if self.zip_file and self.zip_file.name:
            zip_path = self.zip_file.path
            zip_path = zip_path.replace(' ', '_')
            self.title = self.title.replace(' ', '_')
            extract_to = os.path.join('media', 'flipPDF', self.title)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            
            os.remove(zip_path)
            self.zip_file = None

    def set_index_file(self):
        extract_path = os.path.join('media', 'flipPDF', self.title)
        index_file = os.path.join(extract_path, 'index.html')
        
        if os.path.exists(index_file):
            self.index_file = os.path.relpath(index_file, settings.MEDIA_ROOT)

    def set_cover_file(self):
        extract_path = os.path.join('media', 'flipPDF', self.title, 'files', 'pageConfig')
        cover_file = os.path.join(extract_path, '111111111.png')
        
        if os.path.exists(cover_file):
            self.cover_file = os.path.relpath(cover_file, settings.MEDIA_ROOT)
    
    # def delete(self, *args, **kwargs):
    #     # Hapus folder direktori buku FlipPDF
    #     flipPDF_dir = os.path.join('media', 'flipPDF', self.title)
    #     if os.path.exists(flipPDF_dir):
    #         try:
    #             for root, dirs, files in os.walk(flipPDF_dir, topdown=False):
    #                 for file in files:
    #                     os.remove(os.path.join(root, file))
    #                 for dir in dirs:
    #                     os.rmdir(os.path.join(root, dir))
    #             os.rmdir(flipPDF_dir)
    #         except Exception as e:
    #             logger.error(f"Gagal menghapus direktori {flipPDF_dir}: {str(e)}")
        
    #     # Panggil method delete asli
    #     super().delete(*args, **kwargs)




# Table Materi Guru
class MateriGuru(models.Model):
    id = models.AutoField(primary_key=True)
    nama_materi = models.CharField(max_length=100)
    file_materi = models.FileField(upload_to='materi/')
    mata_pelajaran = models.ForeignKey(MataPelajaran, on_delete=models.CASCADE)
    guru = models.ForeignKey(Guru, on_delete=models.CASCADE)
    sekolah = models.ForeignKey(Sekolah, on_delete=models.CASCADE)
    kelas = models.ForeignKey(JenjangDanKelas, on_delete=models.CASCADE)
    cover_image = models.ImageField(upload_to='materi_covers/', blank=True, null=True, editable=False)
    status = models.BooleanField(choices=[(True, 'Aktif'), (False, 'Tidak Aktif')], default=False, null=True)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            # Simpan model terlebih dahulu
            super().save(*args, **kwargs)
            
            # Buat cover image jika belum ada
            if self.file_materi and not self.cover_image:
                try:
                    cover_image = create_cover_image(self.file_materi.path)
                    self.cover_image.save(f"cover_{self.nama_materi}.jpg", cover_image, save=False)
                    super().save(update_fields=['cover_image'])
                except Exception as e:
                    print(f"Error saat membuat cover: {str(e)}")

    def __str__(self):
        return self.nama_materi
    
    def delete(self, *args, **kwargs):
        if self.cover_image:
            if os.path.isfile(self.cover_image.path):
                os.remove(self.cover_image.path)
        
        if self.file_materi:
            if os.path.isfile(self.file_materi.path):
                os.remove(self.file_materi.path)
                
        super().delete(*args, **kwargs)

def create_cover_image(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File tidak ditemukan: {file_path}")

    try:
        pdf_document = fitz.open(file_path)
        first_page = pdf_document[0]
        pix = first_page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        thumb_io = BytesIO()
        img.save(thumb_io, 'JPEG', quality=85)
        thumb_io.seek(0)
        
        return File(thumb_io, name=f"{os.path.splitext(os.path.basename(file_path))[0]}_cover.jpg")
    finally:
        if 'pdf_document' in locals():
            pdf_document.close()

# Table Perangkat Kurikulum
class PerangkatKurikulum(models.Model):
    id = models.AutoField(primary_key=True)
    nama_pk = models.CharField(max_length=100)
    file_pk = models.FileField(upload_to='PK/')
    mata_pelajaran = models.ForeignKey(MataPelajaran, on_delete=models.CASCADE)
    guru = models.ForeignKey(Guru, on_delete=models.CASCADE)
    sekolah = models.ForeignKey(Sekolah, on_delete=models.CASCADE)
    
    def delete(self, *args, **kwargs):
        if self.file_pk:
            if os.path.isfile(self.file_pk.path):
                os.remove(self.file_pk.path)
                
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.nama_pk



