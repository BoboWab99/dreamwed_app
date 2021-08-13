from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse

from main.decorators import unauthenticated_user
from main.settings import LOGIN_URL, HOME
from dreamwed.models import User


def home(request):
   if not request.user.is_authenticated:
      return render(request, 'dreamwed/index.html')

   user_id = request.user.id
   if request.user.is_vendor:
      return redirect('user-profile', user_id=user_id)
   else:
      return redirect('checklist-all', user_id=user_id)


@login_required
def user_profile(request, user_id):
   requested_user = User.objects.get(id=user_id)
   curr_user = request.user

   if not requested_user.id == curr_user.id:
      return HttpResponse('You do not have access to this account!')

   if curr_user.is_vendor:
      return render(request, 'vendor/profile.html')

   elif curr_user.is_wedding_planner:
      return render(request, 'wedplanner/profile.html')


@unauthenticated_user
def register(request):
   return render(request, 'dreamwed/register.html')


@unauthenticated_user
def user_login(request):
   if not request.method == 'POST':
      return render(request, 'dreamwed/login.html', context={'form': AuthenticationForm()})

   form = AuthenticationForm(data=request.POST)
   if not form.is_valid():
      # throw error: Invalid username or password
      return redirect(LOGIN_URL)

   username = form.cleaned_data['username']
   password = form.cleaned_data['password']
   user = authenticate(username=username, password=password)
   if user is None:
      # throw error: Invalid username or password
      return redirect(LOGIN_URL)

   login(request, user)
   return redirect(HOME)


@login_required
def user_logout(request):
   logout(request)
   return redirect(HOME)