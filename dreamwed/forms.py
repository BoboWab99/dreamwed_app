from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.forms.widgets import DateInput

from dreamwed.models import User, Vendor, WeddingPlanner, Guest, Todo, BudgetItem, Review, VendorCategory, VendorImageUpload


# WEDDING VENDOR TYPES 
VENDOR_CATEGORY_CHOICES = []
categories = VendorCategory.objects.all()

for category in categories:
   VENDOR_CATEGORY_CHOICES += [
      (category.id, category.name),
   ]


class VendorRegForm(UserCreationForm):
   """vendor registration form"""
   first_name = forms.CharField(required=True)  
   last_name = forms.CharField(required=True)
   email = forms.EmailField(required=True)

   business_name = forms.CharField(required=True)
   category = forms.ChoiceField(choices=VENDOR_CATEGORY_CHOICES)
   description = forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'cols': 30}))
   services_offered = forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'cols': 30}))
   city = forms.CharField(required=True)
   location = forms.CharField(required=True) # street code

   class Meta(UserCreationForm.Meta):
      model = User

   @transaction.atomic
   def save(self):
      user = super().save(commit=False)
      user.is_vendor = True
      user.first_name = self.cleaned_data['first_name']
      user.last_name = self.cleaned_data['last_name']
      user.email = self.cleaned_data['email']
      user.save()

      vendor = Vendor.objects.create(user=user)
      vendor.business_name = self.cleaned_data['business_name']
      vendor.category_id = self.cleaned_data['category']
      vendor.description = self.cleaned_data['description']
      vendor.services_offered = self.cleaned_data['services_offered']
      vendor.city = self.cleaned_data['city']
      vendor.location = self.cleaned_data['location']

      vendor.save()
      print(f'\nNew vendor, {vendor.business_name}, saved successfully!\n')
      return user


class WeddingPlannerRegForm(UserCreationForm):
   """wedding planner registration form"""
   first_name = forms.CharField(required=True)  
   last_name = forms.CharField(required=True)
   email = forms.EmailField(required=True)
   wedding_date = forms.DateField(
      required=False, 
      widget=DateInput(attrs={'type': 'date'}),
      )

   class Meta(UserCreationForm.Meta):
      model = User

   @transaction.atomic
   def save(self):
      user = super().save(commit=False)
      user.is_wedding_planner = True
      user.first_name = self.cleaned_data['first_name']
      user.last_name = self.cleaned_data['last_name']
      user.email = self.cleaned_data['email']
      user.save()

      wedding_planner = WeddingPlanner.objects.create(user=user)
      wedding_planner.wedding_date = self.cleaned_data['wedding_date']

      wedding_planner.save()
      print(f'\nNew vendor, {wedding_planner.user}, saved successfully!\n')
      return user



class UserAccountInfoUpdateForm(ModelForm):
   class Meta:
      model = User
      fields = ['username', 'first_name', 'last_name', 'email', 'profile']


class BusinessProfileUpdateForm(ModelForm):
   class Meta:
      model = Vendor
      fields = ['business_name', 'category', 'description', 'services_offered', 'city', 'location']


class VendorImageUploadForm(ModelForm):
   class Meta:
      model = VendorImageUpload
      fields = ['image', 'caption']



class TodoForm(ModelForm):
   """Create new Todo form"""
   class Meta:
      model = Todo
      fields = ['content', 'category', 'due_date']
      widgets = {
         'due_date': DateInput(attrs={'type': 'date'}),
      }


class BudgetItemForm(ModelForm):
   """Add new wedding expense form"""
   class Meta:
      model = BudgetItem
      fields = ['description', 'expense_category', 'cost']


class ReviewForm(ModelForm):
   """Rate wedding vendor services form"""
   class Meta:
      model = Review
      fields = ['stars', 'comment']


class GuestForm(ModelForm):
   """Add new guest form"""
   class Meta:
      model = Guest
      fields = ['name', 'email', 'phone_number', 'rsvp']