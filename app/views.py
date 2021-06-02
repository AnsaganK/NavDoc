from django.shortcuts import render, redirect

from .forms import DepartmentForm, UserForm, ServiceNoteForm
from .models import Department, ServiceNote, Role, Tags, NoteFiles, NoteUsers
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required

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
    notes = NoteUsers.objects.filter(user=user).order_by("-pk")
    for note in notes:
        if note.note.user_index == note.index:
            if note.status == None:
                notStatus.append(note.note)
            elif note.status == success:
                successStatus.append(note.note)
            elif note.status == edit:
                editStatus.append(note.note)
            else:
                errorStatus.append(note.note)
    return render(request, "home.html", {"notStatus": notStatus[:5],"successStatus": successStatus[:5], "editStatus":editStatus[:5], "errorStatus": errorStatus[:5]})

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
    notes = NoteUsers.objects.filter(user=request.user).order_by('-pk')
    result = []
    for note in notes:
        if note.note.user_index == note.index:
            result.append(note.note)
    return render(request, 'my_notes.html', {"notes": result})


def my_note_detail(request, pk):
    note = ServiceNote.objects.get(pk=pk)
    return render(request, "my_note_detail.html", {"note": note})

@login_required()
def notes_list(request):
    # user = request.user
    # notes = user.sign_notes.all()
    last = ServiceNote.objects.last()
    tags = Tags.objects.all()
    notes = ServiceNote.objects.filter(user=request.user).order_by('-pk')
    users = User.objects.all()
    if last:
        number = last.number+1 if last.number else 1
    else:
        number = 1
    return render(request, 'notes.html', {"users": users, "notes": notes, "tags": tags, "number": number})


@login_required()
def tags_list(request):
    tags = Tags.objects.all()
    return render(request, "tags.html", {"tags": tags})

@login_required()
def note_detail(request, pk):
    note = ServiceNote.objects.get(pk=pk)
    return render(request, "note_detail.html", {"note": note})


@login_required()
def edit_status_note(request):
    if request.method == "POST":
        post = request.POST
        note_id = post["note_id"][0]
        status = post['status'][0]
        comment = post['comment'][0]
        note = ServiceNote.objects.get(pk=note_id)
        user_note = NoteUsers.objects.filter(user=request.user).filter(note=note).first()
        if status == success:
            users = note.users.all()
            user_note.comment = comment
            user_note.status = success
            if users.last()["pk"] < user_note.index:
                note.user_index += 1
                note.save()
        elif status == edit:
            user_note.comment = comment
            user_note.status = edit
        elif status == error:
            user_note.comment = comment
            user_note.status = error
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


@login_required()
def user_detail(request, pk):
    user = User.objects.get(pk=pk)
    return render(request, "user_detail.html", {"user": user})


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