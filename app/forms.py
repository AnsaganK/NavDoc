from django import forms
from .models import Department, ServiceNote, Tags, Profile
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ('name', 'picture')


class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1',)


class ServiceNoteForm(forms.ModelForm):
    class Meta:
        model = ServiceNote
        fields = ('number', 'title', 'text', 'fast', 'summa', 'date')

class ServiceNoteEditForm(forms.ModelForm):
    class Meta:
        model = ServiceNote
        fields = ('title', 'text', 'fast', 'summa', 'date')

class TagForm(forms.ModelForm):
    class Meta:
        model = Tags
        fields = '__all__'


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("patronymic","position","mobile","birth_date","signature")


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email',)