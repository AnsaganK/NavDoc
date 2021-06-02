from datetime import datetime, timezone

from django import template
import json
import random

from bs4 import BeautifulSoup as BS

from app.models import NoteUsers
from app.views import role_chef_name

register = template.Library()


@register.filter(name="department_chefs")
def department_chefs(users_list):
    users_str = 'Руководителя нет  '
    if users_list:
        users_list = users_list.filter(role__code=role_chef_name)
        if len(users_list)==1:
            users_str = 'Руководитель: '
        elif len(users_list)>1:
            users_str = 'Руководители: '
        for i in users_list:
            users_str+=i.user.first_name[0]+"."+i.user.last_name+", "
        return users_str[:-2]
    return users_str

@register.filter(name="isSignature")
def isSignature(note, user):
    user_note = NoteUsers.objects.filter(note = note, user=user).first()
    if user_note:
        status = user_note.status
        if status != "success":
            return True
    return False

@register.filter(name="htmlToText")
def htmlToText(data):
    if data.startswith("<"):
        text = BS(data)
        return text.get_text()
    else:
        return data