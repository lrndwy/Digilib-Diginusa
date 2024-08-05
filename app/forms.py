from django import forms
from django.contrib.auth.models import User
from .models import *

class SiswaForm(forms.ModelForm):
    nama = forms.CharField(max_length=255)
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    
    class Meta:
        model = Siswa
        fields = ['nama', 'kelas']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['username'].initial = self.instance.user.username
            self.fields['email'].initial = self.instance.user.email
    
    def save(self, commit=True):
        siswa = super().save(commit=False)
        user = siswa.user
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            siswa.save()
        return siswa

class ImportSiswaForm(forms.Form):
    file = forms.FileField()
    

class GuruForm(forms.ModelForm):
    nama = forms.CharField(max_length=100)
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    
    class Meta:
        model = Guru
        fields = ['nama']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['username'].initial = self.instance.user.username
            self.fields['email'].initial = self.instance.user.email
    
    def save(self, commit=True):
        guru = super().save(commit=False)
        user = guru.user
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            guru.save()
        return guru

class ImportGuruForm(forms.Form):
    file = forms.FileField()
    

class FlipPDFForm(forms.ModelForm):
    class Meta:
        model = FlipPDF
        fields = ['title', 'zip_file', 'kelas', 'mata_pelajaran', 'status', 'untuk']
        widgets = {
            'untuk': forms.Select(attrs={'help_text': 'Kosongkan untuk umum'})
        }
        
class BukuForm(forms.ModelForm):
    class Meta:
        model = Buku
        fields = ['nama_buku', 'file_buku', 'penerbit', 'kelas', 'mata_pelajaran', 'status', 'untuk']
        widgets = {
            'untuk': forms.Select(attrs={'help_text': 'Kosongkan untuk umum'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['untuk'].required = False
        self.fields['untuk'].help_text = 'Kosongkan untuk umum'