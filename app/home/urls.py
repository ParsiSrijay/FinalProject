from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path('home',views.index,name ='index'),
    path('',views.index,name=''),
    path('login/',views.user_login,name='login'),
    path('register',views.reg,name='register'),
    path('portal',views.portal,name='portal'),
    path('logout',views.logout_view,name='logout'),
    path('shgLogin',views.SHGPortal,name='SHGPortal'),
    path('portal1',views.portal1,name='portal1'),
]
