from django.conf.urls import include, url
from django.contrib import admin
from .views import Home, success, failure
from . import views

urlpatterns = [

    url('', Home),
    url('success', views.success),
    url('failure', views.failure,name='failure'),

]