from django.contrib import admin
from .models import Profile, Role, Department, ServiceNote, Tags, NoteFiles, NoteUsers, ServiceNoteTypes, Currency

admin.site.register(Profile)
admin.site.register(Role)
admin.site.register(Department)
admin.site.register(ServiceNote)
admin.site.register(Tags)
admin.site.register(NoteFiles)
admin.site.register(NoteUsers)
admin.site.register(ServiceNoteTypes)
admin.site.register(Currency)
