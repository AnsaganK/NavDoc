from django.conf.urls import url
from django.urls import path, include
from django.views.generic import TemplateView

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
    path("counting/status", counting_status, name="counting_status"),
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
    path('send_push', send_web_push),
    path('webpush/', include('webpush.urls')),
    path('sw.js', TemplateView.as_view(template_name='new_design/sw.js', content_type='application/x-javascript'))

]

urlpatterns+=[
    path("new/send", new_send, name="new_send"),
    path("new/my", new_my, name="new_my"),
    path("new/counting", new_counting, name="new_counting"),
    path("new/departments", new_departments, name="new_departments"),
    path("new/users", new_users, name="new_users"),
    path("new/tags", new_tags, name="new_tags"),
    path("new/roles", new_roles, name="new_roles"),
    path("new/profile", new_profile, name="new_profile"),
    path("new/calendar", new_calendar, name="new_calendar"),


    path("fetch/notes", FetchNotesList.as_view(), name="FetchNotesList"),
    path("fetch/my/notes", FetchMyNotesList.as_view(), name="FetchMyNotesList"),
    path("fetch/counting", FetchCountingList.as_view(), name="FetchCountingList"),
    path("fetch/departments", FetchDepartmentList.as_view(), name="FetchDepartmentList"),
    path("fetch/calendar", FetchCalendar.as_view(), name="FetchCalendar"),

    path("fetch/notes/edit", FetchNoteEdit.as_view(), name="FetchNoteEdit"),
    path("fetch/notes/<int:pk>", FetchNoteDetail.as_view(), name="FetchNoteDetail"),

    path("fetch/tag/edit", FetchTagEdit.as_view(), name="FetchTagEdit"),
    path("fetch/tag/delete/<int:pk>", FetchTagDelete.as_view(), name="FetchTagDelete"),
    path("fetch/tag/create", FetchTagCreate.as_view(), name="FetchTagCreate"),

    path("fetch/department/edit", FetchDepartmentEdit.as_view(), name="FetchDepartmentEdit"),
    path("fetch/department/delete/<int:pk>", FetchDepartmentDelete.as_view(), name="FetchDepartmentDelete"),
    path("fetch/department/create", FetchDepartmentCreate.as_view(), name="FetchDepartmentCreate"),
    path("fetch/department/<int:pk>/users", FetchDepartmentUsers.as_view(), name="FetchDepartmentUsers"),

    path("fetch/users/<int:pk>", FetchUserDetail.as_view(), name="FetchUserDetail"),
    path("fetch/user/edit", FetchUserEdit.as_view(), name="FetchUserEdit"),
    path("fetch/user/delete/<int:pk>", FetchUserDelete.as_view(), name="FetchUserDelete"),
    path("fetch/user/create", FetchUserCreate.as_view(), name="FetchUserCreate"),

    path("fetch/note/create", FetchNoteCreate.as_view(), name="FetchNoteCreate"),
    path("fetch/note/status", FetchUserAgree.as_view(), name="FetchUserAgree"),

    path("fetch/counting/agree/<int:pk>", FetchBuhAgree.as_view(), name="FetchBuhAgree"),
]