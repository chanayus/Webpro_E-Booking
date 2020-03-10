from webbrowser import register

from django.contrib import admin
from room.models import Room, Booking
from django.contrib.auth.models import Permission

# Register your models here.

class RoomAdmin(admin.ModelAdmin):
    list_display =  ['room_id','name','open_time','close_time','capacity']
    list_per_page = 20
    
    list_filter = ['room_id','name','open_time','close_time','capacity']
    search_fields = ['name']
admin.site.register(Room, RoomAdmin)

class BookingAdmin(admin.ModelAdmin):
    list_display =  ['book_id','room_id','date','start_time','end_time','status','book_by','book_date']
    list_per_page = 20
    
    list_filter = ['book_id','room_id','date','start_time','end_time','status','book_by','book_date']
    search_fields = ['book_id']

admin.site.register(Booking,BookingAdmin)

admin.site.register(Permission)