from django.conf import settings
from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils.html import format_html

from .forms import ImportSiswaForm
from .models import *
from .utils import process_excel_file_siswa


# Register your models here.
class MateriGuruAdmin(admin.ModelAdmin):
    list_display = ('nama_materi', 'guru', 'mata_pelajaran', 'status')
    list_editable = ('status',)
    list_filter = ('status',)
    search_fields = ('nama_materi', 'guru__nama', 'mata_pelajaran__nama')
    
class BukuAdmin(admin.ModelAdmin):
    list_display = ('nama_buku', 'kelas', 'mata_pelajaran', 'status', 'untuk')
    list_editable = ('status',)
    list_filter = ('status', 'kelas', 'mata_pelajaran')
    search_fields = ('judul', 'kelas', 'jenjang')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "untuk":
            kwargs["help_text"] = "Kosongkan untuk umum"
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(Buku, BukuAdmin)
admin.site.register(MateriGuru, MateriGuruAdmin)
admin.site.register(Sekolah)
admin.site.register(MataPelajaran)
admin.site.register(PerangkatKurikulum)
admin.site.register(JenjangDanKelas)

@admin.register(FlipPDF)
class FlipPDFAdmin(admin.ModelAdmin):
    list_display = ('title', 'kelas', 'render_link', 'status')
    search_fields = ('title', 'kelas')
    list_editable = ('status',)

    def render_link(self, obj):
        url = reverse('flippdf_render', args=[obj.id])
        return format_html('<a href="{}">Render FlipPDF</a>', url)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "untuk":
            kwargs["help_text"] = "Kosongkan untuk umum"
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    render_link.short_description = 'Render'

@admin.register(Guru)
class GuruAdmin(admin.ModelAdmin):
    list_display = ['nama', 'sekolah', 'user']
    list_filter = ['sekolah__nama']
    search_fields = ['nama', 'sekolah__nama', 'user__username']



@admin.register(Siswa)
class SiswaAdmin(admin.ModelAdmin):
    list_display = ['nama', 'sekolah', 'kelas', 'user']
    list_filter = ['sekolah__nama', 'kelas']
    search_fields = ['nama', 'sekolah__nama']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-excel/', self.import_excel, name='import_excel'),
        ]
        return custom_urls + urls

    def import_excel(self, request):
        if request.method == 'POST':
            form = ImportSiswaForm(request.POST, request.FILES)
            if form.is_valid():
                excel_file = request.FILES['file']
                result = process_excel_file_siswa(excel_file)
                if result['success']:
                    self.message_user(request, 'Data siswa berhasil diimpor')
                else:
                    self.message_user(request, f'Terjadi kesalahan: {result["error"]}', level='error')
                return redirect('..')
        else:
            form = ImportSiswaForm()
        
        context = {
            'form': form,
            'title': 'Import Siswa dari Excel',
            'site_title': self.admin_site.site_title,
            'site_header': self.admin_site.site_header,
        }
        return render(request, 'admin/import_excel_siswa.html', context)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_import_button'] = True
        return super().changelist_view(request, extra_context=extra_context)
    
    change_list_template = 'admin/change_list_siswa.html'

class CustomAdminLoginView(LoginView):
    template_name = settings.ADMIN_LOGIN_TEMPLATE

admin.site.login = CustomAdminLoginView.as_view()