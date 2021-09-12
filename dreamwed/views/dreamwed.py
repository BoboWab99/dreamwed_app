from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.middleware.csrf import get_token

from main.decorators import unauthenticated_user
from main.settings import LOGIN_URL, HOME
from dreamwed.forms import UserAccountInfoUpdateForm, VendorImageUploadForm
from dreamwed.models import VendorImageUpload


def home(request):
   if not request.user.is_authenticated:
      return render(request, 'dreamwed/home.html')

   if request.user.is_vendor:
      return redirect('user-profile')
   else:
      return redirect('checklist-all')


@login_required
def user_profile(request):
   curr_user = request.user

   if curr_user.is_vendor:
      img_form = VendorImageUploadForm()
      images = VendorImageUpload.objects.filter(vendor_id=curr_user.id)
      context = {
         'img_form': img_form,
         # 'img_form_filled': VendorImageUploadForm(list(images.values())[3]),
         'images': images,
      }
      return render(request, 'vendor/profile.html', context)

   elif curr_user.is_wedding_planner:
      return render(request, 'wedplanner/profile.html')


@login_required
def update_user_account_info(request):
   if not request.method == 'POST':
      form = UserAccountInfoUpdateForm(instance=request.user) 
      return render(request, 'dreamwed/update-account-info.html', {'form': form})

   form = UserAccountInfoUpdateForm(request.POST, request.FILES, instance=request.user)
   if not form.is_valid():
      # display error msg
      return redirect(request.META.get('HTTP_REFERER'))

   form.save()
   return redirect('user-profile')


@unauthenticated_user
def register(request):
   return render(request, 'dreamwed/register.html')


@unauthenticated_user
def user_login(request):
   if not request.method == 'POST':
      login_form = AuthenticationForm()
      return render(request, 'dreamwed/login.html', context={'form': login_form})

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


def get_csrf(request):
   return JsonResponse({'csrf_token': get_token(request)}, status=200)