from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def home(request):
    return HttpResponse("<h1>Welcome to CodeMarga</h1>")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('', include('user_management.urls')),
    path('',include('coderun.urls')),
    path('', include('contest_management.urls')),
]
