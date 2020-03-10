from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Room(models.Model):
    room_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    open_time = models.TimeField()
    close_time =  models.TimeField()
    capacity = models.IntegerField()
    def __str__(self):
        return 'Room name : %s'%(self.name)
    


class Booking(models.Model):
    book_id = models.AutoField(primary_key=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    date = models.DateField()
    start_time =  models.TimeField()
    end_time =  models.TimeField()
    description = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=50)
    status_remark = models.TextField(null=True, blank=True)
    book_by = models.ForeignKey(User, on_delete=models.CASCADE)
    book_date = models.DateField()
    def __str__(self):
        return 'Booking id : %s'%(self.book_id)
