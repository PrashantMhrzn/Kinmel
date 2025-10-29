from django.urls import path
from .views import *

urlpatterns = [
    path('home/', home, name='home'),
    path('login/', login, name='login'),
    path('register/', register, name='register'),
]