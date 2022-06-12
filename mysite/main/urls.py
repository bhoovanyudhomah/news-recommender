from django.urls import path

from . import views #import views from current directory
from django.urls import path, re_path

urlpatterns = [
# The home page
    path('', views.index, name='index'),
    
    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),
]
