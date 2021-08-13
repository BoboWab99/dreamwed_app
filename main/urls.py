"""main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from dreamwed.views import dreamwed, vendor, wedplanner
from main.settings import LOGIN_URL, LOGOUT_URL


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dreamwed.urls')),
    path('U/register/', dreamwed.register, name='register'),
    path('U/register/vendor', vendor.VendorRegView.as_view(), name='vendor-register'),
    path('U/register/wedding-planner', wedplanner.WeddingPlannerRegView.as_view(), name='wedding-planner-register'),
    path('U/login/', dreamwed.user_login, name=LOGIN_URL),
    path('U/logout/', dreamwed.user_logout, name=LOGOUT_URL),
]
