from django import forms
from .models import Department, ServiceNote
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ('name',)


class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1',)


class ServiceNoteForm(forms.ModelForm):
    class Meta:
        model = ServiceNote
        fields = ('number', 'title', 'text', 'fast', 'summa', 'date')