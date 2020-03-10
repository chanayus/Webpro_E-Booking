from django.urls import path
from . import views

urlpatterns = [
    # For user
    path('', views.index, name='index'),
    path('detail/<int:id>/', views.detail, name='detail'),
    path('request/<int:user_id>/', views.room_request, name='request'),
    # For admin
    path('manage/', views.manage, name='manage'),
    path('edit_add/<int:id>/', views.edit_add, name='edit_add'),
    path('delete/<int:id>/', views.delete_room, name='delete_room'),
    path('accept/', views.accept, name='accept'),
    path('accept_detail/<int:id>', views.accept_detail, name='accept_detail'),
]
