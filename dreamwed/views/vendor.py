from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.contrib.auth import login
from django.views.generic import CreateView

from main.decorators import unauthenticated_user
from dreamwed.models import User
from dreamwed.forms import VendorRegForm


@method_decorator(unauthenticated_user, name='dispatch')
class VendorRegView(CreateView):
   model = User
   form_class = VendorRegForm
   template_name = 'dreamwed/vendor-register.html'

   def form_valid(self, form):
      user = form.save()
      login(self.request, user)
      return redirect('user-profile', user_id=user.id)