from django.db import models
from django.db.models.deletion import CASCADE, SET_NULL
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from datetime import datetime
from phonenumber_field.modelfields import PhoneNumberField


class VendorCategory(models.Model):
   """Model representing a wedding vendor category. 
   Vendor categories are added by the Admin in the database. """
   name = models.CharField(max_length=200, help_text='Select a category (EG: Wedding venue)')
   
   def __str__(self):
      return self.name


class User(AbstractUser):
   """Model representing a general system user"""
   is_vendor = models.BooleanField(default=False)
   is_wedding_planner = models.BooleanField(default=False)

   class Meta:
      ordering = ['last_name', 'first_name']

   def get_absolute_url(self):
      """Return the url to access a particular user"""
      return reverse('user-details', args=[str(self.id)])

   def __str__(self):
      return f'{self.first_name} {self.last_name}'


class Vendor(models.Model):
   """Model representing a system user who is a vendor"""
   user = models.OneToOneField(User, on_delete=CASCADE, primary_key=True)
   business_name = models.CharField(max_length=100)
   category = models.ForeignKey(
      VendorCategory, 
      on_delete=SET_NULL, 
      null=True, 
      help_text='Select a category for your business.',
      )

   description = models.TextField(max_length=5000)
   services_offered = models.TextField(max_length=5000)
   city = models.CharField(max_length=500)
   location = models.CharField(max_length=200) # street code

   def get_absolute_url(self):
      """Return the url to access a particular vendor"""
      return reverse('vendor-details', args=[str(self.id)])

   def __str__(self):
      return f'{self.user}: {self.business_name}'


class WeddingPlanner(models.Model):
   """Model representing a user who's planning a wedding"""
   user = models.OneToOneField(User, on_delete=CASCADE, primary_key=True)
   wedding_date = models.DateField(blank=True, null=True)

   def __str__(self):
      return f'{self.user}'


class Todo(models.Model):
   """Model representing a to-do task during wedding planning"""
   wedplanner = models.ForeignKey(WeddingPlanner, on_delete=models.CASCADE)
   content = models.TextField(max_length=5000)
   category = models.ForeignKey(VendorCategory, on_delete=SET_NULL, blank=True, null=True)
   due_date = models.DateField(
      blank=True, 
      null=True, 
      help_text='When would you like to have this done?',
      )
      
   completed = models.BooleanField(
      default=False, 
      help_text='Mark this task as completed.',
      )

   def __str__(self):
      return f'{self.wedplanner}: {self.content}'


class Bookmark(models.Model):
   """Model representing a user who's planning a wedding"""
   wedplanner = models.ForeignKey(WeddingPlanner, on_delete=models.CASCADE)
   vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)

   class Meta:
      unique_together = ('wedplanner', 'vendor',)

   def __str__(self):
      return f'{self.wedplanner}, {self.vendor}'


class Guest(models.Model):
   """Model representing a wedding guest"""
   PENDING = 'P'
   ATTENDING = 'A'
   DECLINED = 'D'

   RSVP_STATUS_CHOICES = [
      (PENDING, 'Pending'),
      (ATTENDING, 'Attending'),
      (DECLINED, 'Declined'),
   ]

   wedplanner = models.ForeignKey(WeddingPlanner, on_delete=models.CASCADE)
   name = models.CharField(max_length=50)
   email = models.EmailField(max_length=128)
   phone_number = PhoneNumberField(blank=True, null=True, unique=True)
   rsvp = models.CharField(
      max_length=1, 
      choices=RSVP_STATUS_CHOICES, 
      default=PENDING, 
      help_text='rsvp status',
      )
   # HANDLE PLUS-ONES

   class Meta:
      ordering = ['rsvp']

   def __str__(self):
      return f'{self.wedplanner}: {self.name}'


class ExpenseCategory(models.Model):
   """Model representing a wedding expense category.
   Some general expense categories are pre-defined by the admin in the System.
   However, users have the right to add more categories of their own"""
   name = models.CharField(max_length=200, help_text='Categorize your expenses for proper budgeting.')
   wedplanner = models.ForeignKey(WeddingPlanner, on_delete=CASCADE, blank=True, null=True)

   def __str__(self):
      return self.name


class BudgetItem(models.Model):
   """Model representing an wedding budget item"""
   wedplanner = models.ForeignKey(User, on_delete=models.CASCADE)
   expense_category = models.ForeignKey(ExpenseCategory, on_delete=SET_NULL, blank=True, null=True)
   description = models.TextField(max_length=500)
   cost = models.FloatField(
      blank=True, 
      null=True,
      help_text='What is the estimated cost of this budget item?',
      )
   paid = models.FloatField(
      blank=True, 
      null=True,
      help_text='How much have you paid for this budget item so far?',
      )

   @property
   def is_balance_cleared(self):
      if self.paid and self.cost == self.paid:
         return True
      return False

   def __str__(self):
      return f'{self.wedplanner}: {self.description}'


class Review(models.Model):
   """Model representing a wedding planner rating of a vendor's service"""
   wedplanner = models.ForeignKey(WeddingPlanner, on_delete=models.CASCADE)
   vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
   stars = models.SmallIntegerField()
   comment = models.TextField(max_length=5000)
   date_posted = models.DateTimeField(default=datetime.now)

   class Meta:
      ordering = ['date_posted']

   def __str__(self):
      return f'{self.wedplanner} to {self.vendor}: {self.comment}'