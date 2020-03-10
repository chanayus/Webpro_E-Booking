from builtins import object
from datetime import date, datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.handlers.modwsgi import groups_for_user
from django.contrib.auth.models import Group, User
from django.shortcuts import redirect, render
from django.template.context_processors import request
from room.models import Booking, Room

# Create your views here.



def register(request):
    context = {}
    if request.method == "POST":
        user_check = User.objects.filter(username=request.POST.get('username'))
        if user_check:
            context['error'] = 'มี username นี้อยู่ในระบบอยู่แล้ว!'
        elif request.POST.get('password') == request.POST.get('confirm'):
            user = User.objects.create_user(username=request.POST.get('username'), email=request.POST.get('email'), 
            password=request.POST.get('password'), first_name=request.POST.get('firstname'), last_name=request.POST.get('lastname') ) # สร้าง uesr ใหม่โดยดึง username และ password จาก form
            group = Group.objects.get(name='User')  # ดีงค่าชนิดของ user จาก form
            group.user_set.add(user)  # เพิ่ม user เข้า group
            context['success'] = 'สร้าง Account สำเร็จ!'
        else:
            context['error'] = 'รหัสผ่านไม่ถูกต้อง!'

    return render(request, 'authen/register.html', context=context)


def my_login(request):
    context = {}

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            group = request.user.groups.all()

            if user.is_superuser or group[0].name == "Admin":
                return redirect('../../manage/')

            elif group[0].name == "User":
                return redirect('../../')

        else:
            context['username'] = username
            context['password'] = password
            context['error'] = 'username หรือ password ไม่ถูกต้อง'
    next_url = request.GET.get('next')
    if next_url:
        context['next_url'] = next_url

    return render(request, 'authen/login.html', context=context)



def my_logout(request):
    logout(request)
    return redirect('login')
