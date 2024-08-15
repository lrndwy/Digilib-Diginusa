from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    
    # Auth
    path('login/', views.login_siswa_dan_guru, name='login_siswa_dan_guru'),
    path('logout/', views.logout_user, name='logout_user'),
    
    # Render
    path('baca/<int:buku_id>/', views.render_buku, name='render_buku'),
    path('flippdf/<int:flipbook_id>/render/', views.flippdf_render, name='flippdf_render'),
    path('materi/<int:materi_id>/', views.render_materi, name='render_materi'),
    
    # Guru
    path('guru/', views.dashboard_guru, name='dashboard_guru'),
    path('guru/dashboard/', views.dashboard_guru, name='dashboard_guru'),
    path('guru/tentang-akun', views.tentang_akun_guru, name='tentang_akun_guru'),
    path('guru/buku/', views.crud_buku, name='crud_buku'),
    path('guru/materi/', views.crud_materi, name='crud_materi'),
    path('guru/perangkat-kurikulum/', views.crud_perangkat_kurikulum, name='crud_perangkat_kurikulum'),
    path('guru/flippdf/', views.crud_flippdf, name='crud_flippdf'),
    
    # Siswa
    path('siswa/', views.dashboard, name='dashboard'),
    path('siswa/dashboard/', views.dashboard, name='dashboard'),
    path('siswa/tentang-akun', views.tentang_akun, name='tentang_akun'),
    
    path('download-excel-template/', views.download_excel_template, name='download_excel_template'),

]