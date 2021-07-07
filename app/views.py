# from datetime import datetime
import datetime
import json

import requests
from django.db.models import F
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView

from rest_framework import status
from django.db.models import Q
from django.views.generic.base import View
from rest_framework.authentication import SessionAuthentication
from rest_framework.parsers import FileUploadParser
from wkhtmltopdf.views import PDFTemplateResponse

from .forms import DepartmentForm, UserForm, ServiceNoteForm, TagForm, UserEditForm, ProfileForm, ServiceNoteEditForm
from .models import Department, ServiceNote, Role, Tags, NoteFiles, NoteUsers, Profile
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required

from rest_framework import viewsets, generics
from rest_framework.views import APIView

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import Http404

from bs4 import BeautifulSoup as BS

from .serializers import ServiceNoteSerializer, ServiceMyNoteSerializer, ServiceMyNoteDetailSerializer, \
    UserInfoSerializer, UserNoteDetailSerializer, DepartmentSerializer, TagSerializer, ProfileSerializer, \
    CreateUserSerializer, CreateServiceNoteSerializer
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

role_employee_name = 'employee'
role_chef_name = 'chef'
role_buh_name = 'buh'
role_admin_name = 'admin'

success = "success"
edit = "edit"
error = "error"


def send_push(token, title, data):
    headers = {'User-Agent': 'Mozilla/5.0',
               'Content-Length': '33333',
               "Accept-Encoding": "gzip, deflate, br",
               "Accept": "*/*",
               "Connection": "keep-alive",
               "Authorization": "key=AAAA1_8zEyw:APA91bGoDNunqFMhw9vMzImDqkhT3raBdpjVJkdYmUwkxRt1IpeoTjZHSUe11i2jYvxQQDeCzxRdSp-gCipfUPfVQpHfevAxlpUVYsPYfJ66d_WfDbwQXBRcbzmgygMZtiziwCpV1kTc",
               "Content-Type": "application/json",
               }
    body = {
        "to": token,
        "notification": {
            "title": title,
            "body": data
        },
        "data": {
            "click_action": "FLUTTER_NOTIFICATION_CLICK",
        }
    }
    data = requests.post("https://fcm.googleapis.com/fcm/send", headers=headers, data=json.dumps(body))
    return data.text


@login_required()
def home(request):
    if "design" in request.COOKIES and request.COOKIES["design"] == "new":
        return redirect("/new/send")

    user = request.user
    notStatus = []
    successStatus = []
    editStatus = []
    errorStatus = []
    notes = NoteUsers.objects.filter(user=user).filter(note__user_index__gte=F('index')).order_by("-pk")
    if request.user.profile.isChef:
        notes = notes.filter(note__isBuh=True)

    for note in notes:
        if note.status == None:
            notStatus.append(note.note)
        elif note.status == success:
            successStatus.append(note.note)
        elif note.status == edit:
            editStatus.append(note.note)
        else:
            errorStatus.append(note.note)
    return render(request, "home.html",
                  {"notStatus": notStatus[:5], "successStatus": successStatus[:5], "editStatus": editStatus[:5],
                   "errorStatus": errorStatus[:5]})


@login_required()
def calendar(request):
    days = {}
    notes = ServiceNote.objects.all().order_by("-pk")

    date_now = datetime.datetime.now() + datetime.timedelta(days=1)
    for i in range(31):
        date_current = date_now - datetime.timedelta(days=1)
        date_now = date_current
        data = notes.filter(date_create__date=date_current.date())
        days[date_current.date()] = data
    return render(request, 'calendar.html', {'days': days})


@login_required()
def chat(request):
    return render(request, 'chat.html')


@login_required()
def departments_list(request):
    departments = Department.objects.all()
    my_department_pk = False
    if request.user.profile.role and request.user.profile.role.code == role_chef_name:
        my_department_pk = request.user.profile.department.pk
    return render(request, 'departments.html', {"departments": departments, "my_department_pk": my_department_pk})


@login_required()
def my_notes_list(request):
    notes = NoteUsers.objects.filter(user=request.user).filter(note__user_index__gte=F('index')).order_by('-pk')

    if request.user.profile.isChef:
        notes = notes.filter(note__isBuh=True)

    count_all = notes.count()
    count_wait = notes.filter(status=None).count()
    count_fast = notes.filter(status=None).filter(note__fast=True).count()
    count_success = notes.filter(status=success).count()
    count_edit = notes.filter(status=edit).count()
    count_error = notes.filter(status=error).count()
    count_files = notes.filter(~Q(note__files=None)).count()

    if request.user.profile.isChef:
        count_wait = notes.filter(status=None).filter(note__isBuh=True).count()
        count_fast = notes.filter(status=None).filter(note__fast=True).filter(note__isBuh=True).count()

    q = "all"
    if request.GET:
        try:
            q = request.GET.get("status")
        except:
            q = "all"
        if q == "wait":
            notes = notes.filter(status=None)
        elif q == "fast":
            notes = notes.filter(status=None).filter(note__fast=True)
        elif q == "success":
            notes = notes.filter(status=success)
        elif q == "edit":
            notes = notes.filter(status=edit)
        elif q == "error":
            notes = notes.filter(status=error)
        elif q == "files":
            notes = notes.filter(~Q(note__files=None))

    paginator = Paginator(notes, 15)  # 3 поста на каждой странице
    page = request.GET.get('page')
    try:
        notes = paginator.page(page)
    except PageNotAnInteger:
        # Если страница не является целым числом, поставим первую страницу
        notes = paginator.page(1)
    except EmptyPage:
        # Если страница больше максимальной, доставить последнюю страницу результатов
        notes = paginator.page(paginator.num_pages)

    return render(request, 'my_notes.html', {"notes": notes,
                                             "count_all": count_all,
                                             "count_wait": count_wait,
                                             "count_fast": count_fast,
                                             "count_success": count_success,
                                             "count_edit": count_edit,
                                             "count_error": count_error,
                                             "count_files": count_files,
                                             "page": page,
                                             "status_name": q
                                             })


@login_required()
def my_note_detail(request, pk):
    note = ServiceNote.objects.get(pk=pk)
    userNote = NoteUsers.objects.filter(user=request.user).filter(note=note).first()
    if userNote.is_read == False:
        userNote.is_read = True
        userNote.save()
    return render(request, "my_note_detail.html", {"note": note, "userNote": userNote})


@login_required()
def notes_list(request):
    # user = request.user
    # notes = user.sign_notes.all()
    last = ServiceNote.objects.last()
    tags = Tags.objects.all()
    notes = ServiceNote.objects.filter(user=request.user).order_by('-pk')

    count_all = notes.count()
    count_wait = notes.filter(status=None).count()
    count_fast = notes.filter(status=None).filter(fast=True).count()
    count_success = notes.filter(status=success).count()
    count_edit = notes.filter(status=edit).count()
    count_error = notes.filter(status=error).count()
    count_files = notes.filter(~Q(files=None)).count()
    q = "all"

    if request.GET:
        try:
            q = request.GET.get("status")
        except:
            q = "all"
        if q == "wait":
            notes = notes.filter(status=None)

        elif q == "fast":
            notes = notes.filter(status=None).filter(fast=True)
        elif q == "success":
            notes = notes.filter(status=success)
        elif q == "edit":
            notes = notes.filter(status=edit)
        elif q == "error":
            notes = notes.filter(status=error)
        elif q == "files":
            notes = notes.filter(~Q(files=None))

    paginator = Paginator(notes, 15)  # 3 поста на каждой странице
    page = request.GET.get('page')
    try:
        notes = paginator.page(page)
    except PageNotAnInteger:
        # Если страница не является целым числом, поставим первую страницу
        notes = paginator.page(1)
    except EmptyPage:
        # Если страница больше максимальной, доставить последнюю страницу результатов
        notes = paginator.page(paginator.num_pages)

    date = datetime.datetime.now()
    year = date.year
    month = date.month if date.month > 9 else "0" + str(date.month)
    day = date.day if date.day > 9 else "0" + str(date.day)
    current_date = f"{year}-{month}-{day}"
    users = User.objects.exclude(profile__isChef=True).order_by("-pk")
    if last:
        number = last.number + 1 if last.number else 1
    else:
        number = 1
    return render(request, 'notes.html', {"users": users, "notes": notes, "tags": tags, "number": number,
                                          "count_all": count_all,
                                          "count_wait": count_wait,
                                          "count_fast": count_fast,
                                          "count_success": count_success,
                                          "count_edit": count_edit,
                                          "count_error": count_error,
                                          "count_files": count_files,
                                          "page": page,
                                          "status_name": q,
                                          "current_date": current_date
                                          })


@login_required()
def tags_list(request):
    tags = Tags.objects.all()
    return render(request, "tags.html", {"tags": tags})


@login_required()
def tag_add(request):
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
    return redirect('tags_list')


@login_required()
def note_detail(request, pk):
    note = ServiceNote.objects.get(pk=pk)
    users = User.objects.exclude(profile__isChef=True)
    tags = Tags.objects.all()
    return render(request, "note_detail.html", {"note": note, "users": users, "tags": tags})


@login_required()
def edit_status_note(request, pk):
    if request.method == "POST":
        post = request.POST
        status = post['status']
        note = ServiceNote.objects.get(pk=pk)
        user_note = NoteUsers.objects.filter(user=request.user).filter(note=note).first()
        if status == success:
            users = note.users.all()
            user_note.status = success
            if user_note.index < len(users):
                new_index = user_note.index + 1
                note.user_index = new_index
                user_next = NoteUsers.objects.filter(note=note).filter(index=new_index).first()
                if user_next.user.profile.isChef:
                    if new_index == len(users) and note.isBuh and user_next.user.profile.token:
                        send_push(user_next.user.profile.token, f"Поступило СЗ №{note.number}", note.title)
                else:
                    if user_next.user.profile.token:
                        send_push(user_next.user.profile.token, f"Поступило СЗ №{note.number}", note.title)
                note.status = None
            elif user_note.index == len(users):
                note.isChef = True
                note.status = success
        elif status == edit:
            user_note.status = edit
            note.status = edit
        elif status == error:
            user_note.status = error
            note.status = error
        if 'comment' in post:
            comment = post['comment']
            user_note.comment = comment
        note.save()
        user_note.save()
    return redirect('my_notes_list')


@login_required()
def users_list(request):
    users = User.objects.order_by("-pk").all()
    return render(request, 'users.html', {'users': users})


@login_required()
def department_archive(request, pk):
    department = Department.objects.get(pk=pk)
    department.archive = not department.archive
    department.save()
    return redirect(department.get_absolute_url())


@login_required()
def department_delete(request, pk):
    if request.user.profile.role and request.user.profile.role.code == role_chef_name or request.user.profile.is_admin:
        department = Department.objects.get(pk=pk)
        department.delete()
    return redirect("departments_list")


@login_required()
def department_edit(request, pk):
    if request.method == "POST":
        department = Department.objects.get(pk=pk)
        department.name = request.POST["name"]
        department.save()
    return redirect(department.get_absolute_url())


@login_required()
def department_add(request):
    if request.method == "POST":
        form = DepartmentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        else:
            print(form.errors)
        return redirect('departments_list')
    return render(request, 'department_add.html')


@login_required()
def department_detail(request, pk):
    department = Department.objects.get(pk=pk)
    chef_users = User.objects.filter(profile__role__code=role_chef_name).filter(profile__department=department)
    employee_users = User.objects.filter(profile__role__code=role_employee_name).filter(profile__department=department)
    shef = False
    if request.user in chef_users or request.user.profile.is_admin:
        shef = True
    return render(request, "department_detail.html",
                  {"department": department, 'chef_users': chef_users, 'employee_users': employee_users, "shef": shef})


def userNameValid(username):
    user = User.objects.filter(username=username)
    if user:
        return True
    return False


def emailValid(email):
    user = User.objects.filter(email=email)
    if user:
        return True
    return False


@login_required()
def user_add(request):
    roles = Role.objects.all()
    departments = Department.objects.all()
    if request.method == "POST":
        form = UserForm(request.POST)
        userNameFound = userNameValid(request.POST["username"])
        emailFound = emailValid(request.POST["email"])
        passwordCheck = request.POST["password1"] != request.POST["password2"]
        if form.is_valid() and not (emailFound or passwordCheck):
            user = form.save()
            profile = user.profile
            profile.department = Department.objects.get(pk=int(request.POST["department"]))
            profile.role = Role.objects.get(pk=int(request.POST["role"]))
            profile.save()
            # login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect("users_list")
        else:
            print(form.errors)
            return render(request, "user_add.html",
                          {"userNameFound": userNameFound, "passwordCheck": passwordCheck, "emailFound": emailFound,
                           "roles": roles, "departments": departments})

    return render(request, "user_add.html", {"roles": roles, "departments": departments})


# @login_required()
# def user_detail(request, pk):
#    user = User.objects.get(pk=pk)
#    return render(request, "user_detail.html", {"user": user})


@login_required()
def profile(request):
    user = request.user

    signature = user.profile.signature

    return render(request, "profile.html", {"user": user})


@login_required()
def service_note_add(request):
    if request.method == "POST":
        post = request.POST
        files = request.FILES
        form = ServiceNoteForm(post)
        if form.is_valid():
            data = form.save()
            data.user = request.user
            for i in files:
                if "input_file" in i:
                    file = files[i]
                    note_file = NoteFiles.objects.create(note=data, file=file)
                    note_file.save()
            for i in post:
                if "tag" in i:
                    tag_id = i.split("_")[-1]
                    tag = Tags.objects.get(pk=tag_id)
                    data.tags.add(tag)
            user_count = 0
            for i in post:
                if "user" in i:
                    user_count += 1
                    index = i.split("_")[1]
                    user_id = post[i]
                    user = User.objects.get(pk=user_id)
                    if index == "1" and user.profile.token:
                        send_push(token=user.profile.token, title=f"Поступило СЗ №{post['number']}", data=post["title"])
                    signer = NoteUsers.objects.create(user=user, index=index, note=data)
                    signer.save()

            chef_user = Profile.objects.filter(isChef=True).first()
            if chef_user:
                user = chef_user.user
                user_count += 1
                signer = NoteUsers.objects.create(user=user, index=user_count, note=data)
                signer.save()
            data.save()
        else:
            print(form.errors)
    return redirect("notes_list")


def service_note_edit(request, pk):
    note = ServiceNote.objects.get(pk=pk)
    note.tags.clear()
    userNote = NoteUsers.objects.filter(status="edit").filter(note=note).filter(note__user_index=F('index')).first()
    if request.method == "POST":
        post = request.POST
        files = request.FILES
        form = ServiceNoteEditForm(request.POST, instance=note)
        if form.is_valid():
            data = form.save()
            data.number = note.number
            data.status = None

            for i in post:
                if "tag" in i:
                    tag_id = i.split("_")[-1]
                    tag = Tags.objects.get(pk=tag_id)
                    data.tags.add(tag)
            userNote.status = None
            note.status = None

            note.save()
            userNote.save()
            # for i in post:
            #    if "user" in i:
            #        index = i.split("_")[1]
            #        user_id = post[i]
            #        user = User.objects.get(pk=user_id)
            #        signer = NoteUsers.objects.create(user=user, index=index, note=data)
            #        signer.save()

    return redirect(note.get_absolute_url())


def generate_notes():
    user = User.objects.get(pk=5)
    user1 = User.objects.get(pk=1)
    user_list = [user, user1]
    for i in range(1, 200):
        last_note = ServiceNote.objects.last()
        last_number = last_note.pk + 1
        if i % 2 == 0:
            note = ServiceNote.objects.create(title="12", user=user, text="Потому что потому что",
                                              date=datetime.datetime.now(),
                                              number=last_number, summa=21334, fast=1)
        else:
            note = ServiceNote.objects.create(title="12", user=user, text="Потому что потому что",
                                              date=datetime.datetime.now(),
                                              number=last_number, summa=21334, fast=0)
        note.user_index = 1
        signer = NoteUsers.objects.create(user=user, index=1, note=note)
        signer1 = NoteUsers.objects.create(user=user1, index=2, note=note)
        signer.save()
        signer1.save()


def all_notes(request):
    notes = ServiceNote.objects.order_by("-pk").all()
    count_all = notes.count()
    count_wait = notes.filter(status=None).count()
    count_fast = notes.filter(status=None).filter(fast=True).count()
    count_success = notes.filter(status=success).count()
    count_edit = notes.filter(status=edit).count()
    count_error = notes.filter(status=error).count()
    if request.GET:
        q = request.GET.get("status")
        if q == "wait":
            notes = notes.filter(status=None)

        elif q == "fast":
            notes = notes.filter(status=None).filter(fast=True)
        elif q == "success":
            notes = notes.filter(status=success)
        elif q == "edit":
            notes = notes.filter(status=edit)
        elif q == "error":
            notes = notes.filter(status=error)

    return render(request, "all_notes.html", {"notes": notes,
                                              "count_all": count_all,
                                              "count_wait": count_wait,
                                              "count_fast": count_fast,
                                              "count_success": count_success,
                                              "count_edit": count_edit,
                                              "count_error": count_error, })


def statistics(request):
    return render(request, "statistics.html")


def counting(request):
    status = "wait"
    if request.GET:
        status = request.GET.get("status")

        if status == "success":
            notes = ServiceNote.objects.filter(isBuh=True).order_by("-pk")
        else:
            notes = ServiceNote.objects.filter(isBuh=False).order_by("-pk")
    else:
        notes = ServiceNote.objects.filter(isBuh=False).order_by("-pk")
    count_wait = ServiceNote.objects.filter(isBuh=False).count()
    count_success = ServiceNote.objects.filter(isBuh=True).count()
    paginator = Paginator(notes, 15)  # 3 поста на каждой странице
    page = request.GET.get('page')
    try:
        notes = paginator.page(page)
    except PageNotAnInteger:
        # Если страница не является целым числом, поставим первую страницу
        notes = paginator.page(1)
    except EmptyPage:
        # Если страница больше максимальной, доставить последнюю страницу результатов
        notes = paginator.page(paginator.num_pages)

    return render(request, "counting.html",
                  {"notes": notes, "page": page, "count_wait": count_wait, "count_success": count_success,
                   "status": status})


def counting_detail(request, pk):
    note = ServiceNote.objects.get(pk=pk)
    return render(request, "buh_note_detail.html", {"note": note})


def counting_status(request):
    if request.method == "POST":
        note_id = request.POST["note"]
        status = request.POST["status"]
        note = ServiceNote.objects.get(pk=int(note_id))
        if status == "success":
            note.isBuh = True
            note.buh = request.user
            if note.user_index == len(note.users.all()):
                chef_user = Profile.objects.filter(isChef=True).first()
                if chef_user.token:
                    send_push(chef_user.token, f"Поступило СЗ №{note.number}", note.title)
        elif status == "error":
            note.isBuh = False
            note.buh = request.user
            note.status = error
        note.save()
        return redirect("counting")


def mobile(request):
    return render(request, "mobile.html")


class CreatePdf(DetailView):
    template = 'note_pdf.html'
    context = {}
    model = ServiceNote

    def get(self, request, *args, **kwargs):
        self.context['note'] = self.get_object()
        self.context['isSignature'] = False
        text = self.get_object().text
        self.context['text'] = text.replace(">", " class='p_first'>", 1) if text.startswith("<p>") or text.startswith(
            "<h1>") or text.startswith("<h2>") or text.startswith("<h3>") else text

        count = self.get_object().users.count()
        if count < 4:
            self.context['top'] = 1200 - (50 * self.get_object().users.count())
        else:
            self.context['top'] = 1200 - (60 * self.get_object().users.count())
        response = PDFTemplateResponse(request=request,
                                       template=self.template,
                                       filename=f"{self.get_object().number}.pdf",
                                       context=self.context,
                                       show_content_in_browser=False,
                                       )
        return response


class CreatePdfSignature(DetailView):
    template = 'note_pdf.html'
    context = {}
    model = ServiceNote

    def get(self, request, *args, **kwargs):
        self.context['note'] = self.get_object()
        self.context['isSignature'] = True
        text = self.get_object().text
        self.context['text'] = text.replace(">", " class='p_first'>", 1) if text.startswith("<p>") or text.startswith(
            "<h1>") or text.startswith("<h2>") or text.startswith("<h3>") else text
        count = self.get_object().users.count()
        if count < 4:
            self.context['top'] = 1200 - (50 * self.get_object().users.count())
        else:
            self.context['top'] = 1200 - (60 * self.get_object().users.count())
        response = PDFTemplateResponse(request=request,
                                       template=self.template,
                                       filename=f"{self.get_object().number}.pdf",
                                       context=self.context,
                                       show_content_in_browser=False,
                                       )
        return response


class ShowPdf(DetailView):
    template = 'note_pdf.html'
    context = {}
    model = ServiceNote

    def get(self, request, *args, **kwargs):
        self.context['note'] = self.get_object()
        self.context['isSignature'] = False
        text = self.get_object().text
        self.context['text'] = text.replace(">", " class='p_first'>", 1) if text.startswith("<p>") or text.startswith(
            "<h1>") or text.startswith("<h2>") or text.startswith("<h3>") else text

        count = self.get_object().users.count()
        if count < 4:
            self.context['top'] = 1200 - (50 * self.get_object().users.count())
        else:
            self.context['top'] = 1200 - (60 * self.get_object().users.count())
        response = PDFTemplateResponse(request=request,
                                       template=self.template,
                                       filename=f"{self.get_object().number}.pdf",
                                       context=self.context,
                                       show_content_in_browser=True,
                                       )
        return response


class ShowPdfSignature(DetailView):
    template = 'note_pdf.html'
    context = {}
    model = ServiceNote

    def get(self, request, *args, **kwargs):
        self.context['note'] = self.get_object()
        self.context['isSignature'] = True
        self.context['chef_signature'] = Profile.objects.filter(
            isChef=True).first().signature.url if Profile.objects.filter(isChef=True).first() and Profile.objects.filter(isChef=True).first().signature else None
        buh = self.get_object().buh
        if buh:
            self.context['buh_signature'] = buh.profile.signature.url
        else:
            self.context['buh_signature'] = None
        text = self.get_object().text
        self.context['text'] = text.replace(">", " class='p_first'>", 1) if text.startswith("<p>") or text.startswith(
            "<h1>") or text.startswith("<h2>") or text.startswith("<h3>") else text
        count = self.get_object().users.count()
        if count < 4:
            self.context['top'] = 1200 - (50 * self.get_object().users.count())
        else:
            self.context['top'] = 1200 - (60 * self.get_object().users.count())
        response = PDFTemplateResponse(request=request,
                                       template=self.template,
                                       filename=f"{self.get_object().number}.pdf",
                                       context=self.context,
                                       show_content_in_browser=True,
                                       )
        return response


@login_required()
def note_download(request, pk):
    note = ServiceNote.objects.get(pk=pk)
    return render(request, "note_pdf.html", {"note": note})


@login_required()
def user_delete(request, pk):
    user = User.objects.get(pk=pk)
    user.delete()
    return redirect("home")


@login_required()
def profile_edit(request, pk):
    user = User.objects.get(pk=pk)
    if request.method == "POST":

        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()

        form2 = ProfileForm(request.POST, request.FILES, instance=user.profile)
        if form2.is_valid():
            form2.save()

        else:
            print(form2.errors)
    if user == request.user:
        return redirect('profile')
    else:
        return redirect(user.profile.get_absolute_url())


@login_required()
def user_detail(request, pk):
    user = User.objects.get(pk=pk)
    return render(request, "profile.html", {"user": user})


@login_required()
def roles(request):
    roles = Role.objects.all()
    return render(request, "roles.html", {"roles": roles})


@login_required()
def role_detail(request, pk):
    role = Role.objects.get(pk=pk)
    return render(request, "role_detail.html", {"role": role})


@login_required()
def search_result(request):
    try:
        q = request.GET.get("q")
    except:
        q = ""
    try:
        send = request.GET.get("send")
    except:
        send = ""

    if send == "on":
        notes = ServiceNote.objects.filter(user=request.user).filter(
            Q(title__icontains=q) | Q(text__icontains=q)).order_by('-pk')
    else:
        notes = NoteUsers.objects.filter(user=request.user).filter(note__user_index__gte=F('index')).filter(
            Q(note__title__icontains=q) | Q(note__text__icontains=q)).order_by('-pk')

    count = notes.count
    paginator = Paginator(notes, 15)  # 3 поста на каждой странице
    page = request.GET.get('page')
    try:
        notes = paginator.page(page)
    except PageNotAnInteger:
        # Если страница не является целым числом, поставим первую страницу
        notes = paginator.page(1)
    except EmptyPage:
        # Если страница больше максимальной, доставить последнюю страницу результатов
        notes = paginator.page(paginator.num_pages)

    return render(request, 'search_result.html', {"notes": notes, "q": q, "page": page, "count": count, "send": send})


class UserLogin(APIView):
    def post(self, request, format=None):
        username = request.data['username']
        password = request.data['password']
        token = request.data['token']
        if not username or not password:
            return Response({'error': 'Нужно заполнить все поля'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if user:
            if token:
                old_user = Profile.objects.filter(token=token).first()
                if old_user:
                    old_user.token = None
                    old_user.save()
                user.profile.token = token
                user.save()
            return Response({
                "user_id": user.id,
            }, status=status.HTTP_200_OK)
        return Response({
            "error": "Пользователь не найден"
        }, status=status.HTTP_404_NOT_FOUND)


class UserDetail(APIView):
    def get(self, request, pk, format=None):
        user = User.objects.get(pk=pk)
        if user:
            serializer = UserInfoSerializer(user)
            return Response(serializer.data)


class NoteList(APIView):
    def get(self, request, pk, format=None):
        user = User.objects.get(pk=pk)
        if user:
            days = 7
            if request.GET:
                try:
                    days = int(request.GET.get('days'))
                except:
                    days = 7
            date = datetime.datetime.now() - datetime.timedelta(days=days)
            notes = ServiceNote.objects.filter(user=user).filter(date__gte=date).order_by('-pk')
            count_all = notes.count()
            count_wait = notes.filter(status=None).count()
            count_fast = notes.filter(status=None).filter(fast=True).count()
            count_success = notes.filter(status=success).count()
            count_edit = notes.filter(status=edit).count()
            count_error = notes.filter(status=error).count()
            serializer = ServiceNoteSerializer(notes, many=True)
            # serializer.data["count_all"] = count_all
            return Response({"notes": serializer.data})


class MyNoteList(APIView):
    def get(self, request, pk, format=None):
        user = User.objects.get(pk=pk)
        if user:
            days = 7
            if request.GET:
                try:
                    days = int(request.GET.get('days'))
                except:
                    days = 7
            date = datetime.datetime.now() - datetime.timedelta(days=days)
            notes = []
            userNotes = NoteUsers.objects.filter(user=user).filter(note__date__gte=date).filter(
                note__user_index__gte=F('index')).order_by('-pk')
            if user.profile.isChef:
                userNotes = userNotes.filter(note__isBuh=True)
            for i in userNotes:
                notes.append(i.note)
            serializer = ServiceMyNoteSerializer(notes, many=True)
            return Response({"notes": serializer.data})


class MyNoteDetail(APIView):
    def get(self, request, pk, format=None):
        note = ServiceNote.objects.filter(pk=pk).first()
        if note.text.startswith("<"):
            text = BS(note.text)
            text = text.get_text()
        else:
            text = note.text
        if note == None:
            return Http404()
        serializer = ServiceMyNoteDetailSerializer(note)
        data = serializer.data
        data["text"] = text
        return Response(data)


class UserNoteDetail(APIView):
    def get(self, request, user_pk, note_pk, format=None):
        noteUser = NoteUsers.objects.filter(user__pk=user_pk).filter(note__pk=note_pk).first()
        if noteUser.note.text.startswith("<"):
            text = BS(noteUser.note.text)
            text = text.get_text()
        else:
            text = noteUser.note.text
        if noteUser.note == None:
            return Http404()
        serializer = UserNoteDetailSerializer(noteUser)
        serializer.data["note"]["text"] = text
        return Response(serializer.data)


class NoteEditStatus(APIView):
    def post(self, request, format=None):
        data = request.data
        user_id = data['user_id']
        note_id = data['note_id']
        comment = data['comment']
        status = data['status']

        user = User.objects.get(pk=user_id)
        note = ServiceNote.objects.get(pk=note_id)
        user_note = NoteUsers.objects.filter(user=user).filter(note=note).first()
        if status == success:
            users = note.users.all()
            user_note.status = success
            if user_note.index < len(users):
                new_index = user_note.index + 1
                note.user_index = new_index
                user_next = NoteUsers.objects.filter(note=note).filter(index=new_index).first()
                if user_next.user.profile.isChef:
                    if new_index == len(users) and note.isBuh and user_next.user.profile.token:
                        send_push(user_next.user.profile.token, f"Поступило СЗ №{note.number}", note.title)
                else:
                    if user_next.user.profile.token:
                        send_push(user_next.user.profile.token, f"Поступило СЗ №{note.number}", note.title)
                note.status = None
            elif user_note.index == len(users):
                note.status = success
                note.isChef = True
        elif status == edit:
            user_note.status = edit
            note.status = edit
        elif status == error:
            user_note.status = error
            note.status = error
        user_note.comment = comment
        note.save()
        user_note.save()
        return Response({'status': 'success'})



class FetchNotesList(APIView):
    def get(self, request, format=None):
        last = ServiceNote.objects.last()
        tags = Tags.objects.all()
        notes = ServiceNote.objects.filter(user=request.user).order_by('-pk')

        count_all = notes.count()
        count_wait = notes.filter(status=None).count()
        count_fast = notes.filter(status=None).filter(fast=True).count()
        count_success = notes.filter(status=success).count()
        count_edit = notes.filter(status=edit).count()
        count_error = notes.filter(status=error).count()
        count_files = notes.filter(~Q(files=None)).count()
        q = "all"

        if request.GET:
            try:
                q = request.GET.get("status")
            except:
                q = "all"
            if q == "wait":
                notes = notes.filter(status=None)

            elif q == "fast":
                notes = notes.filter(status=None).filter(fast=True)
            elif q == "success":
                notes = notes.filter(status=success)
            elif q == "edit":
                notes = notes.filter(status=edit)
            elif q == "error":
                notes = notes.filter(status=error)
            elif q == "files":
                notes = notes.filter(~Q(files=None))

        paginator = Paginator(notes, 15)  # 3 поста на каждой странице
        page = request.GET.get('page')
        try:
            notes = paginator.page(page)
        except PageNotAnInteger:
            # Если страница не является целым числом, поставим первую страницу
            notes = paginator.page(1)
        except EmptyPage:
            # Если страница больше максимальной, доставить последнюю страницу результатов
            notes = paginator.page(paginator.num_pages)

        date = datetime.datetime.now()
        year = date.year
        month = date.month if date.month > 9 else "0" + str(date.month)
        day = date.day if date.day > 9 else "0" + str(date.day)
        current_date = f"{year}-{month}-{day}"
        users = User.objects.exclude(profile__isChef=True).order_by("-pk")
        if last:
            number = last.number + 1 if last.number else 1
        else:
            number = 1
        serializer = ServiceMyNoteDetailSerializer(notes, many=True)
        return Response({"data": serializer.data, "page": notes.number, "isPrevious": notes.has_previous(),
                         "isNext": notes.has_next()})
        # return render(request, 'notes.html', {"users": users, "notes": notes, "tags": tags, "number": number,
        #                                      "count_all": count_all,
        #                                      "count_wait": count_wait,
        #                                      "count_fast": count_fast,
        #                                      "count_success": count_success,
        #                                      "count_edit": count_edit,
        #                                      "count_error": count_error,
        #                                      "count_files": count_files,
        #                                      "page": page,
        #                                      "status_name": q,
        #                                      "current_date": current_date
        #                                      })


class FetchMyNotesList(APIView):
    def get(self, request, format=None):
        notes = NoteUsers.objects.filter(user=request.user).filter(note__user_index__gte=F('index')).order_by('-pk')

        if request.user.profile.isChef:
            notes = notes.filter(note__isBuh=True)

        count_all = notes.count()
        count_wait = notes.filter(status=None).count()
        count_fast = notes.filter(status=None).filter(note__fast=True).count()
        count_success = notes.filter(status=success).count()
        count_edit = notes.filter(status=edit).count()
        count_error = notes.filter(status=error).count()
        count_files = notes.filter(~Q(note__files=None)).count()

        if request.user.profile.isChef:
            count_wait = notes.filter(status=None).filter(note__isBuh=True).count()
            count_fast = notes.filter(status=None).filter(note__fast=True).filter(note__isBuh=True).count()

        q = "all"
        if request.GET:
            try:
                q = request.GET.get("status")
            except:
                q = "all"
            if q == "wait":
                notes = notes.filter(status=None)
            elif q == "fast":
                notes = notes.filter(status=None).filter(note__fast=True)
            elif q == "success":
                notes = notes.filter(status=success)
            elif q == "edit":
                notes = notes.filter(status=edit)
            elif q == "error":
                notes = notes.filter(status=error)
            elif q == "files":
                notes = notes.filter(~Q(note__files=None))

        paginator = Paginator(notes, 15)  # 3 поста на каждой странице
        page = request.GET.get('page')
        try:
            notes = paginator.page(page)
        except PageNotAnInteger:
            # Если страница не является целым числом, поставим первую страницу
            notes = paginator.page(1)
        except EmptyPage:
            # Если страница больше максимальной, доставить последнюю страницу результатов
            notes = paginator.page(paginator.num_pages)


        serializer = UserNoteDetailSerializer(notes, many=True)
        return Response({"data": serializer.data, "page": notes.number, "isPrevious": notes.has_previous(),
                         "isNext": notes.has_next()})


class FetchCountingList(APIView):
    def get(self, request, format=None):
        if request.GET:
            status = request.GET.get("status")

            if status == "success":
                notes = ServiceNote.objects.filter(isBuh=True).order_by("-pk")
            else:
                notes = ServiceNote.objects.filter(isBuh=False).order_by("-pk")
        else:
            notes = ServiceNote.objects.filter(isBuh=False).order_by("-pk")
        count_wait = ServiceNote.objects.filter(isBuh=False).count()
        count_success = ServiceNote.objects.filter(isBuh=True).count()
        paginator = Paginator(notes, 15)  # 3 поста на каждой странице
        page = request.GET.get('page')
        try:
            notes = paginator.page(page)
        except PageNotAnInteger:
            # Если страница не является целым числом, поставим первую страницу
            notes = paginator.page(1)
        except EmptyPage:
            # Если страница больше максимальной, доставить последнюю страницу результатов
            notes = paginator.page(paginator.num_pages)
        serializer = ServiceMyNoteDetailSerializer(notes, many=True)
        return Response({"data":serializer.data, "page": notes.number, "isPrevious": notes.has_previous(),
                         "isNext": notes.has_next()})
        #return render(request, "counting.html",
        #              {"notes": notes, "page": page, "count_wait": count_wait, "count_success": count_success,
        #               "status": status})

class FetchDepartmentList(APIView):
    def get(self, request, format=None):
        departments = Department.objects.all()
        my_department_pk = False
        if request.user.profile.role and request.user.profile.role.code == role_chef_name:
            my_department_pk = request.user.profile.department.pk
        serializer = DepartmentSerializer(departments, many=True)
        return Response({"data":serializer.data, "my_department_pk": my_department_pk})
        #return render(request, 'departments.html', {"departments": departments, "my_department_pk": my_department_pk})


class FetchNoteDetail(APIView):
    def get(self, request, pk, format=None):
        note = ServiceNote.objects.filter(pk=pk).first()
        serializer = ServiceMyNoteDetailSerializer(note)
        return Response(serializer.data)


class FetchUserDetail(APIView):
    def get(self, request,  pk, format=None):
        user = User.objects.get(pk=pk)
        serializer = UserInfoSerializer(user)
        return Response(serializer.data)


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return None


class FetchTagEdit(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)

    def post(self, request, format=None):
        tag = Tags.objects.filter(pk=int(request.data["pk"])).first()
        if tag:
            tag.name = request.data["name"]
            tag.save()
            serializer = TagSerializer(tag)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"status": "error", "message": "Не найден тэг"}, status=status.HTTP_404_NOT_FOUND)


class FetchTagDelete(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)
    def delete(self, request, pk, format=None):
        tag = Tags.objects.filter(pk=pk).first()
        if tag:
            tag.delete()
            return Response({"message": "Тэг удален"}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "error", "message": "Не найден тэг"}, status=status.HTTP_404_NOT_FOUND)

class FetchTagCreate(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)
    def post(self, request, format=None):
        tag = Tags(name = request.data["name"])
        tag.save()
        serializer = TagSerializer(tag)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FetchCalendar(APIView):
    def get(self, request, format=None):
        try:
            year = int(request.GET.get('year'))
            month = int(request.GET.get('month'))
            day = int(request.GET.get('day'))
        except:
            return Response({"message": "Ошибка"},status=status.HTTP_400_BAD_REQUEST)
        notes = ServiceNote.objects.filter(date_create__year=year,date_create__month=month,date_create__day=day)
        serializer = ServiceMyNoteDetailSerializer(notes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FetchDepartmentEdit(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)

    def post(self, request, format=None):
        department = Department.objects.filter(pk=int(request.data["pk"])).first()
        if department:
            department.name = request.data["name"]
            department.save()
            serializer = DepartmentSerializer(department)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"status": "error", "message": "Не найден отдел"}, status=status.HTTP_404_NOT_FOUND)

class FetchDepartmentDelete(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)

    def delete(self, request, pk, format=None):
        department = Department.objects.filter(pk=pk).first()
        if department:
            department.delete()
            return Response({"message": "Отдел удален"}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "error", "message": "Не найден отдел"}, status=status.HTTP_404_NOT_FOUND)


class FetchDepartmentCreate(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)

    def post(self, request, format=None):
        department = Department(name=request.data["name"])
        department.save()
        serializer = DepartmentSerializer(department)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FetchDepartmentUsers(APIView):
    def get(self, request, pk, format=None):
        department = Department.objects.filter(pk=pk).first()
        if department:
            profiles = department.profiles
            serializer = ProfileSerializer(profiles, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Отдел не найден"}, status=status.HTTP_404_NOT_FOUND)


# КОНТРОЛЛЕРЫ ДЛЯ ПОЛЬЗОВАТЕЛЯ
class FetchUserEdit(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)

    def post(self, request, format=None):
        user = User.objects.filter(pk=int(request.data["pk"])).first()
        if user:
            form = UserForm(request.data, instance=user)
            if form.is_valid():
                user.save()
                serializer = DepartmentSerializer(user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Отправлены не полные данные"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "error", "message": "Не найден пользователь"}, status=status.HTTP_404_NOT_FOUND)

class FetchUserDelete(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)

    def delete(self, request, pk, format=None):
        user = User.objects.filter(pk=pk).first()
        if user:
            user.profile.archive = True
            user.save()
            return Response({"message": "Пользователь удален"}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "error", "message": "Не найден пользователь"}, status=status.HTTP_404_NOT_FOUND)


class FetchUserCreate(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)

    def post(self, request, format=None):
        data = request.data
        error_list = []
        if data["password1"] != data["password2"]:
            error_list.append({"message":"Пароли не совпадают"})

        if User.objects.filter(username=data["username"]):
            error_list.append({"message":"Пользователь с таким логином уже существует"})

        if len(error_list) > 0:
            return Response({"messages": error_list}, status=status.HTTP_400_BAD_REQUEST)

        form = UserForm(request.data)
        if form.is_valid():
            user = form.save()
            department = Department.objects.filter(pk=data["department"]).first()
            if department:
                user.profile.department = department
                user.save()
            serializer = CreateUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            error_list.append({"message": "Отправлены не валидные данные"})
            return Response({"messages":error_list}, status=status.HTTP_400_BAD_REQUEST)

class FetchNoteCreate(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)

    def post(self, request, format=None):
        post = request.data
        files = request.FILES
        form = ServiceNoteForm(post)
        if form.is_valid():
            data = form.save()
            data.user = request.user
            for i in files:
                if "input_file" in i:
                    file = files[i]
                    note_file = NoteFiles.objects.create(note=data, file=file)
                    note_file.save()
            for i in post:
                if "tag" in i:
                    tag_id = i.split("_")[-1]
                    tag = Tags.objects.get(pk=tag_id)
                    data.tags.add(tag)
            user_count = 0
            for i in post:
                if "user" in i:
                    user_count += 1
                    index = i.split("_")[1]
                    user_id = post[i]
                    user = User.objects.get(pk=user_id)
                    if index == "1" and user.profile.token:
                        send_push(token=user.profile.token, title=f"Поступило СЗ №{post['number']}", data=post["title"])
                    signer = NoteUsers.objects.create(user=user, index=index, note=data)
                    signer.save()

            chef_user = Profile.objects.filter(isChef=True).first()
            if chef_user:
                user = chef_user.user
                user_count += 1
                signer = NoteUsers.objects.create(user=user, index=user_count, note=data)
                signer.save()
            data.save()
            return Response({"message": "СЗ сохранено"}, status=status.HTTP_200_OK)

        else:
            print(form.errors)
            return Response({"message": "Отправлены не валидные данные"}, status=status.HTTP_400_BAD_REQUEST)


class FetchBuhAgree(APIView):
    def get(self, request, pk, format=None):
        if request.user.profile.isBuh:
            note = ServiceNote.objects.filter(pk=pk).first()
            if note:
                note.isBuh = True
                note.buh = request.user
                if note.user_index == len(note.users.all()):
                    chef_user = Profile.objects.filter(isChef=True).first()
                    if chef_user and chef_user.token:
                        send_push(chef_user.token, f"Поступило СЗ №{note.number}", note.title)
                note.save()
                return Response({"message": "Подтверждено"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "СЗ не найдено"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message": "У вас недостаточно прав"}, status=status.HTTP_400_BAD_REQUEST)

def editNoteStatus(note, user_note, status, comment):
    pass


class FetchUserAgree(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)
    def post(self, request, format=None):
        post = request.data
        user = request.user
        note = ServiceNote.objects.filter(pk=post["id"]).first()
        user_note = NoteUsers.objects.filter(user=user).filter(note=note).first()
        comment = post["comment"]
        status = post["status"]
        if note and user_note:
            if status == success:
                users = note.users.all()
                user_note.status = success
                if user_note.index < len(users):
                    new_index = user_note.index + 1
                    note.user_index = new_index
                    user_next = NoteUsers.objects.filter(note=note).filter(index=new_index).first()
                    if user_next.user.profile.isChef:
                        if new_index == len(users) and note.isBuh and user_next.user.profile.token:
                            send_push(user_next.user.profile.token, f"Поступило СЗ №{note.number}", note.title)
                    else:
                        if user_next.user.profile.token:
                            send_push(user_next.user.profile.token, f"Поступило СЗ №{note.number}", note.title)
                    note.status = None
                elif user_note.index == len(users):
                    note.status = success
                    note.isChef = True
            elif status == edit:
                user_note.status = edit
                note.status = edit
            elif status == error:
                user_note.status = error
                note.status = error
            user_note.comment = comment
            note.save()
            user_note.save()
            serializer = ServiceMyNoteDetailSerializer(note)
            return Response(serializer.data)
        else:
            return Response({"message": "СЗ не найдено"}, status=status.HTTP_404_NOT_FOUND)


def new_send(request):
    users = User.objects.filter(profile__archive=False).filter(profile__isChef=False)
    tags = Tags.objects.all()
    last = ServiceNote.objects.last()
    if last:
        number = last.number + 1 if last.number else 1
    else:
        number = 1

    date = datetime.datetime.now()
    year = date.year
    month = date.month if date.month > 9 else "0" + str(date.month)
    day = date.day if date.day > 9 else "0" + str(date.day)
    current_date = f"{year}-{month}-{day}"
    return render(request, "new_design/send.html", {"users":users, "tags": tags, "number": number, "current_date":current_date})


def new_my(request):
    return render(request, "new_design/my.html")


def new_counting(request):
    return render(request, "new_design/counting.html")


def new_departments(request):
    departments = Department.objects.all().order_by("pk")
    return render(request, "new_design/departments.html", {"departments": departments})


def new_users(request):
    users = User.objects.filter(profile__archive=False).order_by("pk").all()
    departments = Department.objects.order_by("pk").all()
    return render(request, "new_design/users.html", {"users": users, "departments":departments})


def new_tags(request):
    tags = Tags.objects.all().order_by("pk")
    return render(request, "new_design/tags.html", {"tags": tags})


def new_roles(request):
    roles = Role.objects.all()
    return render(request, "new_design/roles.html", {"roles": roles})


def new_profile(request):
    user = request.user
    return render(request, "new_design/profile.html", {"user": user})


def new_calendar(request):
    return render(request, "new_design/calendar.html")