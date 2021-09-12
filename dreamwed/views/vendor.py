from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from django.views.decorators.http import require_http_methods

from main.decorators import unauthenticated_user, wedding_vendor_required
from dreamwed.models import User, VendorImageUpload
from dreamwed.forms import VendorRegForm, BusinessProfileUpdateForm, VendorImageUploadForm


@method_decorator(unauthenticated_user, name='dispatch')
class VendorRegView(CreateView):
   model = User
   form_class = VendorRegForm
   template_name = 'dreamwed/vendor-register.html'

   def form_valid(self, form):
      user = form.save()
      login(self.request, user)
      return redirect('user-profile')



@login_required 
@wedding_vendor_required
def update_business_profile(request):
   if not request.method == 'POST':
      form = BusinessProfileUpdateForm(instance=request.user.vendor) 
      return render(request, 'vendor/update-business-profile.html', {'form': form})

   form = BusinessProfileUpdateForm(request.POST, request.FILES, instance=request.user.vendor)
   if not form.is_valid():
      # display error msg
      return redirect(request.META.get('HTTP_REFERER'))

   form.save()
   return redirect('user-profile')


@login_required 
@wedding_vendor_required
@require_http_methods('POST')
def upload_picture(request):
   img_form = VendorImageUploadForm(request.POST, request.FILES)
   if not img_form.is_valid():
      # error msg
      return redirect(request.META.get('HTTP_REFERER'))

   image = img_form.cleaned_data['image']
   caption = img_form.cleaned_data['caption']
   new_img = VendorImageUpload(
      vendor_id = request.user.id,
      image=image,
      caption=caption,
   )
   new_img.save()
   return redirect(request.META.get('HTTP_REFERER'))


@login_required 
@wedding_vendor_required
@require_http_methods('POST')
def update_picture(request, img_id):
   img_form = VendorImageUploadForm(request.POST, request.FILES)

   if not img_form.is_valid():
      # error msg
      return redirect(request.META.get('HTTP_REFERER'))

   img_to_update = VendorImageUpload.objects.get(id=img_id, vendor_id=request.user.id)
   img_to_update.image = img_form.cleaned_data['image']
   img_to_update.caption = img_form.cleaned_data['caption']

   img_to_update.save()
   return redirect(request.META.get('HTTP_REFERER'))


@login_required 
@wedding_vendor_required
def delete_picture(request, img_id):
   img_to_delete = VendorImageUpload.objects.get(id=img_id, vendor_id=request.user.id)
   img_to_delete.delete()
   return redirect(request.META.get('HTTP_REFERER'))