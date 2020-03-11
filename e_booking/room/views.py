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


# For User-------------------------------------------------------------------------

@login_required
@permission_required('room.add_booking')
def index(request):
    context = {}
    room_exclude = [] #เก็บ id ห้องที่มีการจ้องไว้แล้ว เพื่มนำไป exclude ออก

    time_list = [] #เก็บเวลาเปิด/ปิดของห้องที่มี
    time_id = [] #เก็บ id ของห้องเพื่อเอาไป filter

    room_txt = request.POST.get('room_name', '')
    day_txt = request.POST.get('day', '')
    time_txt = request.POST.get('time', '').split("-")

    room = Room.objects.filter(name__icontains=room_txt)
   
    # ดึงเวลาค่าเดียวในกรณีที่มีห้องเปิดเวลาเดียวกัน
    for i in Room.objects.all(): 
        time_str = str(i.open_time)+" - "+str(i.close_time) #แปลงเวลาเปิด/ปิด ของห้อง เป็น Str
        if time_str not in time_list: #ถ้าค่าของไม่มีเวลาเปิด/ปิดห้อง ใน time_list ก็จะทำการเพิ่ม และ เพิ่ม id ของห้องใน time_id
            time_list.append(time_str)
            time_id.append(i.room_id)

    if request.method == "POST":
        if len(time_txt) != 1 and day_txt:
            # ดึงการจอง ที่มีค่าเท่ากับ ค่าที่ input จาก form
            booking = Booking.objects.filter(date=day_txt, start_time__gte=datetime.strptime(
                time_txt[0], '%H:%M').time(), end_time__gte=datetime.strptime(time_txt[0], '%H:%M').time(), status__in=['รอการอนุมัติ', 'อนุมัติ'])

            # เก็บ id ของห้องที่มีการจองไว้ใน list
            for i in booking:
                room_exclude.append(i.room_id)

            # เอาห้องที่มี id ตรงกับค่าใน room_exclude ออก
            room = Room.objects.exclude(room_id__in=room_exclude)

            # ดึงห้องที่มี เวลาว่างของห้องตรงกับ input
            room = room.filter(open_time=time_txt[0], close_time=time_txt[1])
            
    context['room'] = room
    context['room_time'] = Room.objects.filter(room_id__in=time_id)

    return render(request, 'room/user_index.html', context=context)


@login_required
@permission_required('room.add_booking')
def detail(request, id):
    room = Room.objects.get(pk=id)
    context = {
        'room': room
    }

    if request.method == "POST":
        day = request.POST.get('day')
        # สร้างการจอง
        book = Booking(room_id=id, date=day, start_time=request.POST.get('start'), end_time=request.POST.get('end'), description=request.POST.get(
            'description'), book_by_id=request.user.id, status="รอการอนุมัติ", status_remark=None, book_date=date.today())

        start = datetime.strptime(book.start_time, '%H:%M').time()
        end = datetime.strptime(book.end_time, '%H:%M').time()
        print()

        # เช็คว่าห้องที่จะจอง มีการจองแล้วหรือยัง
        booking = Booking.objects.filter(date=day, room_id=id, status__in=['รอการอนุมัติ', 'อนุมัติ']) 
        if booking:
            context['error'] = 'ห้องนี้มีการจองแล้ว'

        # เช็คว่าเวลาที่จองห้องอยู่ในช่วงเวลา เปิด-ปิด ของห้องหรือไม่
        elif start >= room.open_time and end <= room.close_time:
            book.save()

        else:
            context['error'] = 'โปรดใส่ระยะเวลาการจองให้อยู่ในช่วงเวลา เปิด/ปิด ของห้อง'

    return render(request, 'room/user_detail.html', context=context)


@login_required
@permission_required('room.add_booking')
def room_request(request, user_id):
    context = {
        'booking': Booking.objects.filter(book_by_id=user_id),
    }

    return render(request, 'room/user_room_request.html', context=context)

# For Admin -------------------------------------------------------------------------


@login_required
@permission_required('room.change_room')
def manage(request):
    room = Room.objects.all() 
    if request.method == "GET":
        room = Room.objects.filter(
            name__icontains=request.GET.get('room_name', ''))
    context = {
        'room': room
    }
    return render(request, 'room/admin_manage.html', context=context)


@login_required
@permission_required('room.change_room')
def edit_add(request, id):
    context = {}
    
    # ถ้า id > 0 เข้าเงื่อนไขการแก้ไขห้อง
    if id > 0:  
        room = Room.objects.get(pk=id)
        context = {
            'room': room,
            'check': 'check'
        }
        if request.method == "POST":
            # แก้ไขข้อมูลห้องในฐานข้อมูล
            room.name = request.POST.get('roomname')
            room.open_time = request.POST.get('start')
            room.close_time = request.POST.get('end')
            room.capacity = request.POST.get('capacity')
            room.save()
            return redirect('manage')

    # ถ้า id = 0 เข้าเงื่อนไขการสร้างห้องใหม่
    else:     
        if request.method == "POST":
            new_room = Room(name=request.POST.get('roomname'), open_time=request.POST.get(
                'start'), close_time=request.POST.get('end'), capacity=request.POST.get('capacity'))
            new_room.save()
            return redirect('manage')
    
    return render(request, 'room/admin_edit_add.html', context=context)


@login_required
@permission_required('room.change_room')
def delete_room(request, id):
    # ลบห้องในฐานข้อมูล
    room = Room.objects.get(pk=id)
    room.delete()
    print(room)
    return redirect('manage')


@login_required
@permission_required('room.change_room')
def accept(request):
    context = {
        'booking': Booking.objects.all(),
    }
    return render(request, 'room/admin_accept.html', context=context)


@login_required
@permission_required('room.change_room')
def accept_detail(request, id):
    context = {}
    book = Booking.objects.get(book_id=id)
    user = User.objects.get(id=book.book_by_id)
    
    context['booking'] = book
    context['user_book'] = user

    if request.method == "POST":
        if request.POST.get('action') == 'accept':
            book.status_remark = request.POST.get('description')
            book.status = 'อนุมัติ'
        else:
            book.status_remark = request.POST.get('description')
            book.status = 'ปฏิเสธ'
        book.save()
        context['success'] = 'การอนุมัติ/ปฏิเสธ สำเร็จ!'

    return render(request, 'room/admin_accept_detail.html', context=context)
