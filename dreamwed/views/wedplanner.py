import json

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.views.generic import CreateView
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import connection

from main.decorators import wedding_planner_required, unauthenticated_user
from dreamwed.forms import WeddingPlannerRegForm, TodoForm, GuestForm, BudgetItemForm, VENDOR_CATEGORY_CHOICES
from dreamwed.models import User, Vendor, WeddingPlanner, Guest, Todo, BudgetItem, Bookmark, ExpenseCategory


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


#  VENDORS 
# -------------------------
def vendors(request):
   vendors = Vendor.objects.all()

   if(request.headers.get('X-Requested-With') == 'XMLHttpRequest'):
      if not request.user.is_authenticated:
         response = list(vendors.values())
         return JsonResponse(response, safe=False, status=200)

      raw_query = f'''SELECT * FROM dreamwed_vendor
      LEFT JOIN (SELECT dreamwed_bookmark.wedplanner_id, 
      dreamwed_bookmark.vendor_id AS bookmarked_vendor_id FROM dreamwed_bookmark
      WHERE dreamwed_bookmark.wedplanner_id = {request.user.id}) AS bookmarks
      ON dreamwed_vendor.user_id = bookmarks.bookmarked_vendor_id'''

      response = execute_raw_fetch(raw_query)
      return JsonResponse(response, safe=False, status=200) 

   context = {
      'vendor_categories': VENDOR_CATEGORY_CHOICES,
      'vendors': vendors,
   }
   return render(request, 'wedplanner/vendors.html', context)


def vendor_details(request, vendor_id):
   vendor = Vendor.objects.get(user_id=vendor_id)
   return render(request, 'wedplanner/vendor-details.html', {'vendor': vendor})


#  BOOKMARKS 
# -------------------------
@login_required
@wedding_planner_required
def bookmarks(request):
   bookmarks = Bookmark.objects.values_list('vendor_id', flat=True).filter(wedplanner_id=request.user.id)
   saved_vendors = Vendor.objects.filter(user_id__in=bookmarks)

   if(request.headers.get('X-Requested-With') == 'XMLHttpRequest'):
      raw_query = f'''SELECT * FROM dreamwed_vendor
      INNER JOIN (SELECT dreamwed_bookmark.wedplanner_id, 
      dreamwed_bookmark.vendor_id AS bookmarked_vendor_id FROM dreamwed_bookmark
      WHERE dreamwed_bookmark.wedplanner_id = {request.user.id}) AS bookmarks
      ON dreamwed_vendor.user_id = bookmarks.bookmarked_vendor_id'''

      response = execute_raw_fetch(raw_query)
      return JsonResponse(response, safe=False, status=200)

   return render(request, 'wedplanner/bookmarks.html', {'vendors': saved_vendors})


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
      return redirect('vendors')


#  GUESTLIST 
# -------------------------
@login_required
@wedding_planner_required
def guest_list(request):
   guests = Guest.objects.filter(wedplanner_id=request.user.id)
   form = GuestForm()
   context = {
      'todos': guests,
      'form': form,
   }
   return render(request, 'wedplanner/guestlist.html', context)


#  CHECKLIST 
# -------------------------
@login_required
@wedding_planner_required
def check_list(request):
   all_todos = Todo.objects.filter(wedplanner_id=request.user.id)

   if(request.headers.get('X-Requested-With') == 'XMLHttpRequest'):
      raw_query = f'''SELECT 
      dreamwed_todo.id AS todo_id,
      dreamwed_todo.content,
      dreamwed_todo.due_date,
      dreamwed_todo.completed,
      dreamwed_vendorCategory.id AS vendor_category_id,
      dreamwed_vendorCategory.name AS vendor_category_name
      FROM dreamwed_todo
      INNER JOIN dreamwed_vendorCategory ON dreamwed_todo.category_id = dreamwed_vendorCategory.id
      WHERE dreamwed_todo.wedplanner_id = {request.user.id}'''

      response = execute_raw_fetch(raw_query)
      return JsonResponse(response, safe=False, status=200)

   form = TodoForm()
   context = {
      'todos': all_todos,
      'form': form,
   }
   return render(request, 'wedplanner/checklist.html', context)


@login_required
@wedding_planner_required
def tasks_in_progress(request):
   raw_query = f'''SELECT 
   dreamwed_todo.id AS todo_id,
   dreamwed_todo.content,
   dreamwed_todo.due_date,
   dreamwed_todo.completed,
   dreamwed_vendorCategory.id AS vendor_category_id,
   dreamwed_vendorCategory.name AS vendor_category_name
   FROM dreamwed_todo
   INNER JOIN dreamwed_vendorCategory ON dreamwed_todo.category_id = dreamwed_vendorCategory.id
   WHERE dreamwed_todo.wedplanner_id = {request.user.id} AND dreamwed_todo.completed = False'''

   response = execute_raw_fetch(raw_query)
   return JsonResponse(response, safe=False, status=200)


@login_required
@wedding_planner_required
def tasks_completed(request):
   raw_query = f'''SELECT 
   dreamwed_todo.id AS todo_id,
   dreamwed_todo.content,
   dreamwed_todo.due_date,
   dreamwed_todo.completed,
   dreamwed_vendorCategory.id AS vendor_category_id,
   dreamwed_vendorCategory.name AS vendor_category_name
   FROM dreamwed_todo
   INNER JOIN dreamwed_vendorCategory ON dreamwed_todo.category_id = dreamwed_vendorCategory.id
   WHERE dreamwed_todo.wedplanner_id = {request.user.id} AND dreamwed_todo.completed = True'''

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
def budget_manager(request):
   expenses = BudgetItem.objects.filter(wedplanner_id=request.user)
   form = BudgetItemForm()

   if(request.headers.get('X-Requested-With') == 'XMLHttpRequest'):
      response = list(expenses.values())
      return JsonResponse(response, safe=False, status=200)

   context = {
      'expenses': expenses,
      'expense_categories': ExpenseCategory.objects.all(),
      'form': form,
   }
   return render(request, 'wedplanner/budget-manager.html', context)


@login_required
@wedding_planner_required
def get_budget_items_in_category(request, category_id):
   budget_items = BudgetItem.objects.filter(wedplanner_id=request.user.id, expense_category_id=category_id)
   response = list(budget_items.values())
   return JsonResponse(response, safe=False, status=200)


@login_required
@wedding_planner_required
@require_http_methods('POST')
def create_budget_item(request):
   budget_item_data = json.loads(request.body)
   form = BudgetItemForm(budget_item_data)

   if not form.is_valid():
      return redirect(request.META.get('HTTP_REFERER'))

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
   form = BudgetItemForm(budget_item_data)

   if not form.is_valid():
      return redirect(request.META.get('HTTP_REFERER'))

   budget_item_to_update = BudgetItem.objects.get(id=budget_item_id, wedplanner_id=request.user.id)
   budget_item_to_update.description = form.cleaned_data['description'] 
   budget_item_to_update.expense_category = form.cleaned_data['expense_category'] 
   budget_item_to_update.cost = form.cleaned_data['cost']

   budget_item_to_update.save()
   return JsonResponse({'msg': 'Budget item updated!'}, status=200)


@login_required
@wedding_planner_required
def delete_budget_item(request, budget_item_id):
   budget_item_to_delete = BudgetItem.objects.get(id=budget_item_id, wedplanner_id=request.user.id)
   budget_item_to_delete.delete()
   return JsonResponse({'msg': 'Task deleted!'}, status=200)