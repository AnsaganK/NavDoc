from datetime import datetime, timezone

from django import template
import json
import random

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
