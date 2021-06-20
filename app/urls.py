from django.conf.urls import url
from django.urls import path
from .views import *
from wkhtmltopdf.views import PDFTemplateView


urlpatterns = [
    url(r'^pdf/$', PDFTemplateView.as_view(template_name='note_pdf.html',
                                           filename='my_pdf.pdf'), name='pdf'),
    path("", home, name="home"),
    path("profile", profile, name="profile"),
    path("calendar", calendar, name="calendar"),
    path("chat", chat, name="chat"),
    path("departments", departments_list, name="departments_list"),
    path("tags", tags_list, name="tags_list"),
    path("my-notes", my_notes_list, name="my_notes_list"),
    path("notes", notes_list, name="notes_list"),
    path("users", users_list, name="users_list"),
    path("roles", roles, name="roles"),
    path("roles/<int:pk>", role_detail, name="role_detail"),
    path("statistics", statistics, name="statistics"),
    path("counting", counting, name="counting"),
    path("counting/<int:pk>", counting_detail, name="counting_detail"),
    path("mobile", mobile, name="mobile"),
    path("departments/add", department_add, name="department_add"),
    path("departments/edit/<int:pk>", department_edit, name="department_edit"),
    path("departments/delete/<int:pk>", department_delete, name="department_delete"),
    path("departments/archive/<int:pk>", department_archive, name="department_archive"),
    path("departments/<int:pk>", department_detail, name="department_detail"),
    path("users/add", user_add, name="user_add"),
    path("user/delete/<int:pk>", user_delete, name="user_delete"),
    path("user/edit/<int:pk>", profile_edit, name="profile_edit"),
    path("users/<int:pk>", user_detail, name="user_detail"),
    path("tags/add", tag_add, name="tag_add"),
    path("my-notes/<int:pk>", my_note_detail, name="my_note_detail"),
    path("my-notes/status/<int:pk>", edit_status_note, name="edit_status_note"),
    path("notes/add", service_note_add, name="service_note_add"),
    path("notes/edit/<int:pk>", service_note_edit, name="service_note_edit"),
    path("notes/<int:pk>", note_detail, name="note_detail"),
    path("search", search_result, name="search_result"),
    path("notes/download/<int:pk>", CreatePdf.as_view(), name="note_download"),
    path("notes/download/isSignature/<int:pk>", CreatePdfSignature.as_view(), name="note_signature_download"),

    path("notes/show/<int:pk>", ShowPdf.as_view(), name="note_show"),
    path("notes/show/isSignature/<int:pk>", ShowPdfSignature.as_view(), name="note_signature_show"),
    path("all-notes", all_notes, name="all_notes"),
]