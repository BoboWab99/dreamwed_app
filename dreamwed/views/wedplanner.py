import json
import datetime as DT

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.views.generic import CreateView
from django.http import JsonResponse
from django.db.models import Avg, Sum
from django.views.decorators.http import require_http_methods
from django.db import connection

from main.decorators import wedding_planner_required, unauthenticated_user
from dreamwed.forms import WeddingPlannerRegForm, TodoForm, GuestForm, BudgetItemForm, WeddingPlannerProfileUpdateForm, ReviewForm, BudgetItemUpdateForm, UpdateGuestForm, WeddingBudgetForm
from dreamwed.models import User, Vendor, WeddingPlanner ,VendorCategory, Review, Guest, Todo, BudgetItem, Bookmark, ExpenseCategory, VendorImageUpload


def dictfetchall(cursor):
   "Return all rows from a cursor as a dict: Django Docs"
   columns = [col[0] for col in cursor.description]
   return [
      dict(zip(columns, row))
      for row in cursor.fetchall()
   ]

def execute_raw_fetch(raw_query):
   result = [] 
   with connection.cursor() as cursor:
      cursor.execute(raw_query)
      result = dictfetchall(cursor)
   return result


def verified_vendors():
   ''' Verified vendors have at least 3 business pictures '''
   enough_pics = 3
   verified_vendors_ids = []
   all_vendors_ids = Vendor.objects.values_list('user_id')

   for vendor_id in all_vendors_ids:
      this_vendor_pics = VendorImageUpload.objects.filter(vendor_id=vendor_id).count()
      if (this_vendor_pics > enough_pics):
         verified_vendors_ids.append(vendor_id[0])

   return tuple(verified_vendors_ids)


#  VENDORS 
# -------------------------
def vendors(request):
   if(not request.headers.get('X-Requested-With') == 'XMLHttpRequest'):
      vendor_categories = VendorCategory.objects.all()
      context = {'vendor_categories': vendor_categories}
      return render(request, 'wedplanner/vendors.html', context)

   verified = f'''
   SELECT
      dreamwed_user.profile,
      dreamwed_vendor.user_id AS vendor_id,
      dreamwed_vendor.business_name,
      dreamwed_vendor.location,
      dreamwed_vendor.city
   FROM dreamwed_vendor
   INNER JOIN dreamwed_user
      ON dreamwed_vendor.user_id = dreamwed_user.id
      AND dreamwed_vendor.user_id IN {verified_vendors()} '''

   verified_vendors_data = execute_raw_fetch(verified)

   for verified_vendor in verified_vendors_data:
      vendor_id  = verified_vendor['vendor_id']
      num_reviews = Review.objects.filter(vendor_id=vendor_id).count()
      avrg_rating = Review.objects.filter(vendor_id=vendor_id).aggregate(Avg('stars'))
      verified_vendor['num_reviews'] = num_reviews
      verified_vendor['avrg_rating'] = avrg_rating['stars__avg']
      verified_vendor['is_vendor_bookmarked'] = False

      if request.user.is_authenticated:
         bookmark = Bookmark.objects.filter(wedplanner_id=request.user.id, vendor_id=vendor_id)
         if bookmark:
            verified_vendor['is_vendor_bookmarked'] = True

   return JsonResponse(verified_vendors_data, safe=False, status=200) 


def vendor_details(request, vendor_id):
   review_form = ReviewForm()
   vendor = Vendor.objects.get(user_id=vendor_id)
   vendor_reviews = Review.objects.filter(vendor_id=vendor_id)
   images = VendorImageUpload.objects.filter(vendor_id=vendor_id)

   context = {
      'review_form': review_form,
      'vendor': vendor,
      'vendor_images': images,
      'vendor_reviews': vendor_reviews,
   }
   return render(request, 'wedplanner/vendor-details.html', context)


#  BOOKMARKS 
# -------------------------
@login_required
@wedding_planner_required
def bookmarks(request):
   if(not request.headers.get('X-Requested-With') == 'XMLHttpRequest'):
      bookmarks = Bookmark.objects.values_list('vendor_id', flat=True).filter(wedplanner_id=request.user.id)
      saved_vendors = Vendor.objects.filter(user_id__in=bookmarks)
      return render(request, 'wedplanner/bookmarks.html', {'vendors': saved_vendors})

   verified = f'''
   SELECT
      dreamwed_user.profile,
      dreamwed_vendor.user_id AS vendor_id,
      dreamwed_vendor.business_name,
      dreamwed_vendor.location,
      dreamwed_vendor.city
   FROM dreamwed_vendor
   INNER JOIN dreamwed_user
      ON dreamwed_vendor.user_id = dreamwed_user.id
      AND dreamwed_vendor.user_id IN {verified_vendors()} '''

   bookmarked = f'''
   SELECT 
      dreamwed_bookmark.wedplanner_id  AS bookmark_wedplaner_id, 
      dreamwed_bookmark.vendor_id AS bookmark_vendor_id 
   FROM dreamwed_bookmark
   WHERE dreamwed_bookmark.wedplanner_id = {request.user.id} '''

   raw_query = f''' SELECT * 
   FROM ({verified}) AS verified
   INNER JOIN ({bookmarked}) AS bookmarked
   ON verified.vendor_id = bookmarked.bookmark_vendor_id '''

   data = execute_raw_fetch(raw_query)

   for verified_vendor in data:
      vendor_id  = verified_vendor['vendor_id']
      num_reviews = Review.objects.filter(vendor_id=vendor_id).count()
      avrg_rating = Review.objects.filter(vendor_id=vendor_id).aggregate(Avg('stars'))
      verified_vendor['num_reviews'] = num_reviews
      verified_vendor['avrg_rating'] = avrg_rating['stars__avg']
      verified_vendor['is_vendor_bookmarked'] = False

      if request.user.is_authenticated:
         bookmark = Bookmark.objects.filter(wedplanner_id=request.user.id, vendor_id=vendor_id)
         if bookmark:
            verified_vendor['is_vendor_bookmarked'] = True

   return JsonResponse(data, safe=False, status=200)


@login_required
@wedding_planner_required
def bookmark_vendor(request, vendor_id):
   new_bookmark = Bookmark(wedplanner_id=request.user.id, vendor_id=vendor_id)
   new_bookmark.save()
   return JsonResponse({'msg': 'New bookmark added!'})


@login_required
@wedding_planner_required
def delete_bookmarked_vendor(request, vendor_id):
   bookmark = Bookmark.objects.get(wedplanner_id=request.user.id, vendor_id=vendor_id)
   bookmark.delete()
   return JsonResponse({'msg': 'Bookmark deleted!'})


#  REGISTRATION 
# -------------------------
@method_decorator(unauthenticated_user, name='dispatch')
class WeddingPlannerRegView(CreateView):
   model = User
   form_class = WeddingPlannerRegForm
   template_name = 'dreamwed/wedding-planner-register.html'

   def form_valid(self, form):
      user = form.save()
      login(self.request, user)
      messages.success(self.request, 'Registration successful!') 
      return redirect('vendors')


@login_required
@wedding_planner_required
def update_wedplanner_profile(request):
   if not request.method == 'POST':
      form = WeddingPlannerProfileUpdateForm(instance=request.user.weddingplanner) 
      return render(request, 'wedplanner/update-profile-info.html', {'form': form})

   form = WeddingPlannerProfileUpdateForm(request.POST, instance=request.user.weddingplanner) 
   if not form.is_valid():
      messages.error(request, 'Form is not valid!')
      return redirect(request.META.get('HTTP_REFERER'))

   form.save()
   return redirect('user-profile')


#  GUESTLIST 
# -------------------------
@login_required
@wedding_planner_required
def guest_list(request):
   if(request.headers.get('X-Requested-With') == 'XMLHttpRequest'):
      guests = Guest.objects.filter(wedplanner_id=request.user.id)
      data = list(guests.values())
      return JsonResponse(data, safe=False, status=200)

   form = GuestForm()
   context = {'form': form}
   return render(request, 'wedplanner/guestlist.html', context)


@login_required
@wedding_planner_required
@require_http_methods('POST')
def add_guest(request):
   guest_data = json.loads(request.body)
   form = GuestForm(guest_data)

   if not form.is_valid():
      messages.error(request, form.errors)
      return redirect(request.META.get('HTTP_REFERER'))

   guest_name = form.cleaned_data['name']
   guest_email = form.cleaned_data['email']
   guest_phone_number = form.cleaned_data['phone_number']
   guest_rsvp = form.cleaned_data['rsvp']

   new_guest = Guest(
      wedplanner_id=request.user.id,
      phone_number=guest_phone_number,
      name=guest_name,  
      email=guest_email,  
      rsvp=guest_rsvp,
      )
   new_guest.save()
   return JsonResponse({'msg': 'New guest added!'}, status=200)


@login_required
@wedding_planner_required
def update_guest(request, guest_id):
   guest_to_update = Guest.objects.get(id=guest_id, wedplanner_id=request.user.id)

   if not request.method == 'POST':
      guest_form = UpdateGuestForm(instance=guest_to_update)
      return render(request, 'wedplanner/edit-guest.html', {'form': guest_form})

   form = UpdateGuestForm(request.POST)
   if not form.is_valid():
      messages.error(request, form.errors)
      return redirect(request.META.get('HTTP_REFERER'))

   guest_to_update.name = form.cleaned_data['name'] 
   guest_to_update.rsvp = form.cleaned_data['rsvp']
   guest_to_update.note = form.cleaned_data['note']
   guest_to_update.save()
   return redirect('guestlist')


@login_required
@wedding_planner_required
def delete_guest(request, guest_id):
   guest_to_delete = Guest.objects.get(id=guest_id)
   guest_to_delete.delete()
   return JsonResponse({'msg': 'Guest deleted!'}, status=200)


#  CHECKLIST 
# -------------------------
@login_required
@wedding_planner_required
def check_list(request):
   if(request.headers.get('X-Requested-With') == 'XMLHttpRequest'):
      raw_query = f''' 
      SELECT 
         dreamwed_todo.id AS todo_id,
         dreamwed_todo.content,
         dreamwed_todo.due_date,
         dreamwed_todo.completed,
         dreamwed_vendorCategory.id AS vendor_category_id,
         dreamwed_vendorCategory.name AS vendor_category_name
      FROM dreamwed_todo
      INNER JOIN dreamwed_vendorCategory 
         ON dreamwed_todo.category_id = dreamwed_vendorCategory.id
      WHERE dreamwed_todo.wedplanner_id = {request.user.id} '''

      response = execute_raw_fetch(raw_query)
      return JsonResponse(response, safe=False, status=200)

   wedplanner = WeddingPlanner.objects.get(user=request.user)
   form = TodoForm(wedding_date=wedplanner.wedding_date)
   all_todos = Todo.objects.filter(wedplanner_id=request.user.id)
   context = {
      'todos': all_todos,
      'form': form,
   }
   return render(request, 'wedplanner/checklist.html', context)


@login_required
@wedding_planner_required
def tasks_in_progress(request):
   raw_query = f''' 
   SELECT 
      dreamwed_todo.id AS todo_id,
      dreamwed_todo.content,
      dreamwed_todo.due_date,
      dreamwed_todo.completed,
      dreamwed_vendorCategory.id AS vendor_category_id,
      dreamwed_vendorCategory.name AS vendor_category_name
   FROM dreamwed_todo
   INNER JOIN dreamwed_vendorCategory 
      ON dreamwed_todo.category_id = dreamwed_vendorCategory.id
   WHERE dreamwed_todo.wedplanner_id = {request.user.id} 
      AND dreamwed_todo.completed = False '''

   response = execute_raw_fetch(raw_query)
   return JsonResponse(response, safe=False, status=200)


@login_required
@wedding_planner_required
def tasks_completed(request):
   raw_query = f''' 
   SELECT 
      dreamwed_todo.id AS todo_id,
      dreamwed_todo.content,
      dreamwed_todo.due_date,
      dreamwed_todo.completed,
      dreamwed_vendorCategory.id AS vendor_category_id,
      dreamwed_vendorCategory.name AS vendor_category_name
   FROM dreamwed_todo
   INNER JOIN dreamwed_vendorCategory 
      ON dreamwed_todo.category_id = dreamwed_vendorCategory.id
   WHERE dreamwed_todo.wedplanner_id = {request.user.id} 
      AND dreamwed_todo.completed = True '''

   response = execute_raw_fetch(raw_query)
   return JsonResponse(response, safe=False, status=200)


@login_required
@wedding_planner_required
@require_http_methods('POST')
def create_task(request):
   task = json.loads(request.body)
   form = TodoForm(task)

   if not form.is_valid():
      return redirect(request.META.get('HTTP_REFERER'))

   task_content = form.cleaned_data['content']
   task_category = form.cleaned_data['category']
   task_due_date = form.cleaned_data['due_date']

   new_task = Todo(
      wedplanner_id=request.user.id,
      content=task_content, 
      category=task_category,
      due_date=task_due_date, 
      )
   new_task.save()
   return JsonResponse({'msg': 'Task created!'}, status=200)
   

@login_required
@wedding_planner_required
def delete_task(request, task_id):
   task_to_delete = Todo.objects.get(wedplanner_id=request.user.id, id=task_id)
   task_to_delete.delete()
   return JsonResponse({'msg': 'Task deleted!'}, status=200)


@login_required
@wedding_planner_required
@require_http_methods('POST')
def update_task(request, task_id):
   task = json.loads(request.body)
   form = TodoForm(task)

   if not form.is_valid():
      return redirect(request.META.get('HTTP_REFERER'))

   task_to_update = Todo.objects.get(id=task_id, wedplanner_id=request.user.id)
   task_to_update.content = form.cleaned_data['content'] 
   task_to_update.category = form.cleaned_data['category']
   task_to_update.due_date = form.cleaned_data['due_date']
   task_to_update.save()
   return JsonResponse({'msg': 'Task updated!'}, status=200)


@login_required
@wedding_planner_required
def mark_task_as_complete(request, task_id):
   task = Todo.objects.get(id=task_id, wedplanner_id=request.user.id)
   if task.completed == True:
      task.completed = False
   else:
      task.completed = True

   task.save()
   return JsonResponse({'msg': 'Task status changed!'}, status=200)


#  BUDGET MANAGER
# -------------------------
@login_required
@wedding_planner_required
@require_http_methods('POST')
def set_wedding_budget(request):
   budget_data = json.loads(request.body)
   form = WeddingBudgetForm(budget_data)

   if not form.is_valid():
      messages.error(request, form.errors)
      return JsonResponse({'msg:': form.errors.as_text()}, status=200)

   wedplanner = WeddingPlanner.objects.get(user=request.user)
   wedplanner.wedding_budget = form.cleaned_data['wedding_budget']
   wedplanner.save()
   messages.success(request, 'Wedding budget updated!')
   response = {
      'budget': form.cleaned_data['wedding_budget'],
      'msg': 'Wedding budget updated!',
   }
   return JsonResponse(response, status=200)


@login_required
@wedding_planner_required
def budget_manager(request):
   if(request.headers.get('X-Requested-With') == 'XMLHttpRequest'):
      expenses = BudgetItem.objects.filter(wedplanner_id=request.user.id)
      data = list(expenses.values())
      return JsonResponse(data, safe=False, status=200)

   expense_categories = ExpenseCategory.objects.all()
   create_form = BudgetItemForm()
   update_form = BudgetItemUpdateForm()
   budget_form = WeddingBudgetForm(instance=request.user.weddingplanner)

   context = {
      'create_form': create_form,
      'update_form': update_form,
      'budget_form': budget_form,
      'expense_categories': expense_categories,
   }
   return render(request, 'wedplanner/budget-manager.html', context)


@login_required
@wedding_planner_required
def get_budget_items_in_category(request, category_id):
   budget_items = BudgetItem.objects.filter(wedplanner_id=request.user.id, expense_category_id=category_id)
   data = list(budget_items.values())
   return JsonResponse(data, safe=False, status=200)


@login_required
@wedding_planner_required
@require_http_methods('POST')
def create_budget_item(request):
   budget_item_data = json.loads(request.body)
   form = BudgetItemForm(budget_item_data)

   if not form.is_valid():
      return redirect(request.META.get('HTTP_REFERER'))

   wedding_budget = WeddingPlanner.objects.filter(user=request.user).values_list('wedding_budget')[0][0]
   
   budget_item_content = form.cleaned_data['description']
   budget_item_expense_category = form.cleaned_data['expense_category']
   budget_item_cost = form.cleaned_data['cost']

   new_budget_item = BudgetItem(
      wedplanner_id=request.user.id,
      description=budget_item_content, 
      expense_category=budget_item_expense_category, 
      cost=budget_item_cost,
      )
   new_budget_item.save()
   return JsonResponse({'msg': 'Budget item created!'}, status=200)


@login_required
@wedding_planner_required
@require_http_methods('POST')
def update_budget_item(request, budget_item_id):
   budget_item_data = json.loads(request.body)
   form = BudgetItemUpdateForm(budget_item_data)

   if not form.is_valid():
      return redirect(request.META.get('HTTP_REFERER'))

   budget_item_to_update = BudgetItem.objects.get(id=budget_item_id, wedplanner_id=request.user.id)
   budget_item_to_update.description = form.cleaned_data['description'] 
   budget_item_to_update.expense_category = form.cleaned_data['expense_category'] 
   budget_item_to_update.cost = form.cleaned_data['cost']
   budget_item_to_update.paid = form.cleaned_data['paid']
   budget_item_to_update.save()
   return JsonResponse({'msg': 'Budget item updated!'}, status=200)


@login_required
@wedding_planner_required
def delete_budget_item(request, budget_item_id):
   budget_item_to_delete = BudgetItem.objects.get(id=budget_item_id, wedplanner_id=request.user.id)
   budget_item_to_delete.delete()
   return JsonResponse({'msg': 'Task deleted!'}, status=200)


@login_required
@wedding_planner_required
def budget_items_share(request):
   expense_categories = ExpenseCategory.objects.all()
   expense_categories_share = []
   total_paid = BudgetItem.objects.filter(
      wedplanner_id=request.user.id
      ).aggregate(total_paid=Sum('paid'))['total_paid']

   for category in expense_categories:
      category_share = BudgetItem.objects.filter(
         wedplanner_id=request.user.id,
         expense_category=category,
         ).aggregate(total_price=Sum('paid'))['total_price']

      if category_share:
         expense_category = {
            'expense_category_name': category.name,
            'expense_category_share': category_share
         }
         expense_categories_share.append(expense_category)
   
   data = {
      'total_paid': total_paid,
      'expense_categories_share': expense_categories_share,
   }
   return JsonResponse(data, safe=False, status=200)


@login_required
@wedding_planner_required
def my_balance(request):
   wedding_budget = WeddingPlanner.objects.filter(user=request.user).values_list('wedding_budget')[0][0]
   total_paid = BudgetItem.objects.filter(
      wedplanner_id=request.user.id
      ).aggregate(total_paid=Sum('paid'))['total_paid']

   data = {
      'wedding_budget': wedding_budget,
      'total_paid': total_paid,
   }
   return JsonResponse(data, safe=False, status=200)


#  RATE VENDOR
# -------------------------
@login_required
@wedding_planner_required
@require_http_methods('POST')
def save_review(request, vendor_id):
   form = ReviewForm(request.POST)

   if not form.is_valid():
      messages.error(request, 'Form ain\'t valid')
      return redirect(request.META.get('HTTP_REFERER'))

   rating = form.cleaned_data['stars']
   review = form.cleaned_data['comment']

   new_review = Review(
      wedplanner_id=request.user.id,
      vendor_id=vendor_id,
      comment=review, 
      stars=rating, 
      )
   new_review.save()
   return redirect(request.META.get('HTTP_REFERER'))


@login_required
@wedding_planner_required
def update_review(request, review_id):
   review_to_update = Review.objects.get(id=review_id)

   if not request.method == 'POST':
      review_form = ReviewForm(instance=review_to_update)
      return render(request, 'wedplanner/update-review.html', {'form': review_form})

   review_form = ReviewForm(request.POST)
   if not review_form.is_valid():
      messages.error(request, 'Form ain\'t valid')
      return redirect(request.META.get('HTTP_REFERER'))

   review_to_update.comment = review_form.cleaned_data['comment']
   review_to_update.stars = review_form.cleaned_data['stars']
   review_to_update.save()
   return redirect('vendor-details', vendor_id=review_to_update.vendor_id)


@login_required
@wedding_planner_required
def delete_review(request, review_id):
   review_to_delete = Review.objects.get(id=review_id)
   review_to_delete.delete()
   messages.success(request, 'Task successfully deleted!')
   return redirect(request.META.get('HTTP_REFERER'))