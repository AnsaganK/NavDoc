from datetime import datetime
from django.db.models import F
from django.shortcuts import render, redirect
from django.views.generic import DetailView

from rest_framework import status
from django.db.models import Q
from django.views.generic.base import View
from wkhtmltopdf.views import PDFTemplateResponse

from .forms import DepartmentForm, UserForm, ServiceNoteForm, TagForm, UserEditForm, ProfileForm, ServiceNoteEditForm
from .models import Department, ServiceNote, Role, Tags, NoteFiles, NoteUsers
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
    UserInfoSerializer

role_employee_name = 'employee'
role_chef_name = 'chef'
role_buh_name = 'buh'
role_admin_name = 'admin'

success = "success"
edit = "edit"
error = "error"


@login_required()
def home(request):
    user = request.user
    notStatus = []
    successStatus = []
    editStatus = []
    errorStatus = []
    notes = NoteUsers.objects.filter(user=user).filter(note__user_index__gte=F('index')).order_by("-pk")
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
    return render(request, 'calendar.html')


@login_required()
def chat(request):
    return render(request, 'chat.html')


@login_required()
def departments_list(request):
    departments = Department.objects.all()
    return render(request, 'departments.html', {"departments": departments})


@login_required()
def my_notes_list(request):
    notes = NoteUsers.objects.filter(user=request.user).filter(note__user_index__gte=F('index')).order_by('-pk')

    count_all = notes.count()
    count_wait = notes.filter(status=None).count()
    count_fast = notes.filter(status=None).filter(note__fast=True).count()
    count_success = notes.filter(status=success).count()
    count_edit = notes.filter(status=edit).count()
    count_error = notes.filter(status=error).count()
    count_files = notes.filter(~Q(note__files = None)).count()

    if request.GET:
        q = request.GET.get("status")
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

    return render(request, 'my_notes.html', {"notes": notes,
                                          "count_all": count_all,
                                          "count_wait": count_wait,
                                          "count_fast": count_fast,
                                          "count_success": count_success,
                                          "count_edit": count_edit,
                                          "count_error": count_error,
                                          "count_files": count_files,
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
    count_files = notes.filter(~Q(files = None)).count()
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
        elif q == "files":
            notes = notes.filter(~Q(files=None))

    users = User.objects.all()
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
    users = User.objects.all()
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
                note.user_index = user_note.index + 1
                note.status = None
            elif user_note.index == len(users):
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
    users = User.objects.all()
    return render(request, 'users.html', {'users': users})


@login_required()
def department_archive(request, pk):
    department = Department.objects.get(pk=pk)
    department.archive = not department.archive
    department.save()
    return redirect(department.get_absolute_url())


@login_required()
def department_delete(request, pk):
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
        form = DepartmentForm(request.POST)
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
    return render(request, "department_detail.html",
                  {"department": department, 'chef_users': chef_users, 'employee_users': employee_users})


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


#@login_required()
#def user_detail(request, pk):
#    user = User.objects.get(pk=pk)
#    return render(request, "user_detail.html", {"user": user})


@login_required()
def profile(request):
    user = request.user

    signature = user.profile.signature
    sign = signature.read() if signature else None

    return render(request, "profile.html", {"user": user, "signature": sign})


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
            for i in post:
                if "user" in i:
                    index = i.split("_")[1]
                    user_id = post[i]
                    user = User.objects.get(pk=user_id)
                    signer = NoteUsers.objects.create(user=user, index=index, note=data)
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
            #for i in post:
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
            note = ServiceNote.objects.create(title="12", user=user, text="Потому что потому что", date=datetime.now(),
                                              number=last_number, summa=21334, fast=1)
        else:
            note = ServiceNote.objects.create(title="12", user=user, text="Потому что потому что", date=datetime.now(),
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
                                          "count_error": count_error,})


def statistics(request):
    return render(request, "statistics.html")


class CreatePdf(DetailView):
    template='note_pdf.html'
    context = {}
    model = ServiceNote

    def get(self, request, *args, **kwargs):
        self.context['note'] = self.get_object()
        self.context['isSignature'] = False
        text = self.get_object().text
        self.context['text'] = text.replace(">", " class='p_first'>", 1) if text.startswith("<p>") or text.startswith(
            "<h1>") or text.startswith("<h2>") or text.startswith("<h3>") else text


        count = self.get_object().users.count()
        if count<4:
            self.context['top'] = 1200-(50*self.get_object().users.count())
        else:
            self.context['top'] = 1200-(60*self.get_object().users.count())
        response=PDFTemplateResponse(request=request,
                                     template=self.template,
                                     filename=f"{self.get_object().number}.pdf",
                                     context=self.context,
                                     show_content_in_browser=False,
                                     )
        return response

class CreatePdfSignature(DetailView):
    template='note_pdf.html'
    context = {}
    model = ServiceNote

    def get(self, request, *args, **kwargs):
        self.context['note'] = self.get_object()
        self.context['isSignature'] = True
        text = self.get_object().text
        self.context['text'] = text.replace(">", " class='p_first'>", 1) if text.startswith("<p>") or text.startswith("<h1>") or text.startswith("<h2>") or text.startswith("<h3>") else text
        count = self.get_object().users.count()
        if count<4:
            self.context['top'] = 1200-(50*self.get_object().users.count())
        else:
            self.context['top'] = 1200-(60*self.get_object().users.count())
        response=PDFTemplateResponse(request=request,
                                     template=self.template,
                                     filename=f"{self.get_object().number}.pdf",
                                     context=self.context,
                                     show_content_in_browser=False,
                                     )
        return response

class ShowPdf(DetailView):
    template='note_pdf.html'
    context = {}
    model = ServiceNote

    def get(self, request, *args, **kwargs):
        self.context['note'] = self.get_object()
        self.context['isSignature'] = False
        text = self.get_object().text
        self.context['text'] = text.replace(">", " class='p_first'>", 1) if text.startswith("<p>") or text.startswith(
            "<h1>") or text.startswith("<h2>") or text.startswith("<h3>") else text


        count = self.get_object().users.count()
        if count<4:
            self.context['top'] = 1200-(50*self.get_object().users.count())
        else:
            self.context['top'] = 1200-(60*self.get_object().users.count())
        response=PDFTemplateResponse(request=request,
                                     template=self.template,
                                     filename=f"{self.get_object().number}.pdf",
                                     context=self.context,
                                     show_content_in_browser=True,
                                     )
        return response

class ShowPdfSignature(DetailView):
    template='note_pdf.html'
    context = {}
    model = ServiceNote

    def get(self, request, *args, **kwargs):
        self.context['note'] = self.get_object()
        self.context['isSignature'] = True
        text = self.get_object().text
        self.context['text'] = text.replace(">", " class='p_first'>", 1) if text.startswith("<p>") or text.startswith("<h1>") or text.startswith("<h2>") or text.startswith("<h3>") else text
        count = self.get_object().users.count()
        if count<4:
            self.context['top'] = 1200-(50*self.get_object().users.count())
        else:
            self.context['top'] = 1200-(60*self.get_object().users.count())
        response=PDFTemplateResponse(request=request,
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

        form2 = ProfileForm(request.POST,request.FILES, instance=user.profile)
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

class UserLogin(APIView):
    def post(self, request, format=None):
        username = request.data['username']
        password = request.data['password']

        if not username or not password:
            return Response({'error': 'Нужно заполнить все поля'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if user:
            return Response({
                "user_id": user.id,
            }, status=status.HTTP_200_OK)
        return Response({
            "error": "Пользователь не найден"
        }, status=status.HTTP_404_NOT_FOUND)

class UserDetail(APIView):
    def get(self, request,pk, format=None):
        user = User.objects.get(pk=pk)
        if user:
            serializer = UserInfoSerializer(user)
            return Response(serializer.data)

class NoteList(APIView):
    def get(self, request, pk, format=None):
        user = User.objects.get(pk=pk)
        if user:
            notes = ServiceNote.objects.filter(user=user).order_by('-pk')
            count_all = notes.count()
            count_wait = notes.filter(status=None).count()
            count_fast = notes.filter(status=None).filter(fast=True).count()
            count_success = notes.filter(status=success).count()
            count_edit = notes.filter(status=edit).count()
            count_error = notes.filter(status=error).count()
            serializer = ServiceNoteSerializer(notes, many=True)
            #serializer.data["count_all"] = count_all
            return Response({"notes":serializer.data})


class MyNoteList(APIView):
    def get(self, request, pk, format=None):
        user = User.objects.get(pk=pk)
        if user:
            notes = []
            userNotes = NoteUsers.objects.filter(user=user).filter(note__user_index__gte=F('index')).order_by('-pk')
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

#class Login(APIView):
#    def post(self, request, pk, format=None):
