from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.views.generic import CreateView

from main.decorators import vendor_required, unauthenticated_user
from dreamwed.models import User
from dreamwed.forms import VendorRegForm


@login_required
@vendor_required
def vendor_dashboard(request, user_id):
   return render(request, 'vendor/profile.html')


@method_decorator(unauthenticated_user, name='dispatch')
class VendorRegView(CreateView):
   model = User
   form_class = VendorRegForm
   template_name = 'dreamwed/vendor-register.html'

   def form_valid(self, form):
      user = form.save()
      login(self.request, user)
      return redirect('user-profile')