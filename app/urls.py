from django.urls import path
from .views import *

urlpatterns = [
    path("", home, name="home"),
    path("profile", profile, name="profile"),
    path("calendar", calendar, name="calendar"),
    path("chat", chat, name="chat"),
    path("departments", departments_list, name="departments_list"),
    path("my-notes", my_notes_list, name="my_notes_list"),
    path("notes", notes_list, name="notes_list"),
    path("users", users_list, name="users_list"),
    path("departments/add", department_add, name="department_add"),
    path("departments/edit/<int:pk>", department_edit, name="department_edit"),
    path("departments/delete/<int:pk>", department_delete, name="department_delete"),
    path("departments/archive/<int:pk>", department_archive, name="department_archive"),
    path("departments/<int:pk>", department_detail, name="department_detail"),
    path("users/add", user_add, name="user_add"),
    path("users/<int:pk>", user_detail, name="user_detail"),
]