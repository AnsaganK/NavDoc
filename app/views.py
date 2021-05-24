from django.shortcuts import render, redirect

from .forms import DepartmentForm, UserForm
from .models import Department, ServiceNote, Role
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required


role_employee_name = 'employee'
role_chef_name = 'chef'
role_buh_name = 'buh'
role_admin_name = 'admin'

@login_required()
def home(request):
    return render(request, "home.html")

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
    # my_notes = ServiceNote.objects.filter(user=request.user)
    return render(request, 'my_notes.html')

@login_required()
def notes_list(request):
    # user = request.user
    # notes = user.sign_notes.all()
    return render(request, 'notes.html')

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
    return render(request, "department_detail.html", {"department": department, 'chef_users': chef_users, 'employee_users': employee_users})

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
            #login(request, user, backend='django.contrib.auth.backends.ModelBackend')
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
    return render(request, "profile.html", {"user": user})