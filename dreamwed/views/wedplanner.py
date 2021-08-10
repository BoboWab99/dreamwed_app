from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.views.generic import CreateView
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from main.decorators import wedding_planner_required, unauthenticated_user
from main.settings import HOME
from dreamwed.forms import WeddingPlannerRegForm, TodoForm, GuestForm, BudgetItemForm
from dreamwed.models import User, Vendor, WeddingPlanner, Guest, Todo, BudgetItem, Bookmark


# NOT SURE WHERE THIS SHOULD BE DONE
def get_vendor(user_id):
   vendor = None
   vendor_list = Vendor.objects.filter(user_id=user_id)
   if len(vendor_list) > 0:
      vendor = vendor_list[0]

   return vendor


def get_wedding_planner(user_id):
   wedding_planner = None
   wed_planner_list = WeddingPlanner.objects.filter(user_id=user_id)
   if len(wed_planner_list) > 0:
      wedding_planner = wed_planner_list[0]

   return wedding_planner


# ========= VENDORS =========
def vendors(request):
   vendors = Vendor.objects.all()
   return render(request, 'wedplanner/vendors.html', {'vendors': vendors})


def vendor_details(request, user_id):
   vendor = get_vendor(user_id)
   return render(request, 'wedplanner/vendor-details.html', {'vendor': vendor})


# ========= REGISTRATION =========
@method_decorator(unauthenticated_user, name='dispatch')
class WeddingPlannerRegView(CreateView):
   model = User
   form_class = WeddingPlannerRegForm
   template_name = 'dreamwed/wedding-planner-register.html'

   def form_valid(self, form):
      user = form.save()
      login(self.request, user)
      return redirect('vendors')


# ========= GUESTLIST =========
@login_required
@wedding_planner_required
def guest_list(request, user_id):
   guests = Guest.objects.filter(wedplanner_id=request.user.id)
   form = GuestForm()
   context = {
      'todos': guests,
      'form': form,
   }
   return render(request, 'wedplanner/guestlist.html', context)


# ========= CHECKLIST =========
@login_required
@wedding_planner_required
def check_list(request, user_id):
   todos = Todo.objects.filter(user_id=request.user.id)
   form = TodoForm()
   context = {
      'todos': todos,
      'form': form,
   }
   return render(request, 'wedplanner/checklist.html', context)


@login_required
@wedding_planner_required
def tasks_in_progress(request, user_id):
   todos_in_progress = Todo.objects.filter(user_id=request.user.id, completed=False)
   form = TodoForm()
   context = {
      'todos': todos_in_progress,
      'form': form,
   }
   return render(request, 'wedplanner/checklist.html', context)


@login_required
@wedding_planner_required
def tasks_completed(request, user_id):
   completed_todos = Todo.objects.filter(user_id=request.user.id, completed=True)
   form = TodoForm()
   context = {
      'todos': completed_todos,
      'form': form,
   }
   return render(request, 'wedplanner/checklist.html', context)


@login_required
@wedding_planner_required
@require_http_methods('POST')
def create_task(request, user_id):
   form = TodoForm(request.POST)
   if not form.is_valid():
      # FIX: Empty form fields
      return HttpResponse('Form ain\'t valid!')

   task_content = form.cleaned_data['content']
   task_category = form.cleaned_data['category']
   task_cost = form.cleaned_data['cost']
   due_date = form.cleaned_data['due_date']

   new_task = Todo(
      user_id=request.user.id,
      content=task_content, 
      category = task_category,
      cost=task_cost, 
      due_date=due_date, 
      )
   new_task.save()
   return redirect(HOME)
   

@login_required
@wedding_planner_required
def delete_task(request, user_id, task_id):
   task_to_delete = Todo.objects.filter(user_id=request.user.id, id=task_id)
   task_to_delete.delete()
   return redirect(HOME)


@login_required
@wedding_planner_required
@require_http_methods('POST')
def update_task(request, user_id, task_id):
   form = TodoForm(request.POST)
   if not form.is_valid():
      # FIX: Empty form fields
      return HttpResponse('Form ain\'t valid!')

   task_content = form.cleaned_data['content']
   task_category = form.cleaned_data['category']
   task_cost = form.cleaned_data['cost']
   due_date = form.cleaned_data['due_date']

   task_to_update = Todo(
      id=task_id,
      user_id=request.user.id,
      content=task_content, 
      category = task_category,
      cost=task_cost, 
      due_date=due_date,
      )
   task_to_update.save()
   return redirect(HOME)


@login_required
@wedding_planner_required
@require_http_methods('POST')
def mark_task_as_complete(request, user_id, task_id):
   task = Todo.objects.filter(user_id=request.user.id, id=task_id)[0]
   # data = TodoForm(request.POST)
   print(request.POST)
   # task.completed=True
   # task.save()
   return redirect(HOME)


# ========= BUDGETER =========
@login_required
@wedding_planner_required
def budget_manager(request, user_id):
   expenses = BudgetItem.objects.filter(wedplanner_id=request.user)
   form = BudgetItemForm()
   context = {
      'todos': expenses,
      'form': form,
   }
   return render(request, 'wedplanner/budget-manager.html', context)


# ========= BOOKMARKS =========
@login_required
@wedding_planner_required
def bookmarks(request, user_id):
   bookmarks = Bookmark.objects.values_list('vendor_id', flat=True).filter(user_id=request.user.id)
   saved_vendors = Vendor.objects.filter(user_id__in=bookmarks)
   return render(request, 'wedplanner/bookmarks.html', {'vendors': saved_vendors})


@login_required
@wedding_planner_required
def bookmark_vendor(request, user_id, vendor_id):
   pass