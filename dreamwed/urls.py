from django.urls import path
from dreamwed.views import dreamwed, wedplanner, vendor
from main.settings import LOGIN_URL, LOGOUT_URL


# GENERAL
urlpatterns = [
   path('', dreamwed.home, name='home'),
   path('U/register/', dreamwed.register, name='register'),
   path('U/register/vendor', vendor.VendorRegView.as_view(), name='vendor-register'),
   path('U/register/wedding-planner', wedplanner.WeddingPlannerRegView.as_view(), name='wedding-planner-register'),
   path('U/login/', dreamwed.user_login, name=LOGIN_URL),
   path('U/logout/', dreamwed.user_logout, name=LOGOUT_URL),
   path('U/profile/', dreamwed.user_profile, name='user-profile'),

   path('csrf-token/', dreamwed.get_csrf),
]


# WEDDING PLANNERS
urlpatterns += [
   path('vendors/', wedplanner.vendors, name='vendors'),
   path('vendors/<int:vendor_id>/details', wedplanner.vendor_details, name='vendor-details'),
   path('vendors/<int:vendor_id>/bookmark', wedplanner.bookmark_vendor, name='bookmark-vendor'),
   path('vendors/<int:vendor_id>/remove-bookmark', wedplanner.delete_bookmarked_vendor, name='remove-bookmark'),

   path('U/checklist/', wedplanner.check_list, name='checklist-all'),
   path('U/checklist/in-progress/', wedplanner.tasks_in_progress, name='checklist-in-progress'),
   path('U/checklist/completed/', wedplanner.tasks_completed, name='checklist-completed'),
   path('U/create-task/', wedplanner.create_task, name='create-task'),
   path('U/checklist/<int:task_id>/delete', wedplanner.delete_task, name='delete-task'),
   path('U/checklist/<int:task_id>/update', wedplanner.update_task, name='update-task'),
   path('U/checklist/<int:task_id>/mark-complete', wedplanner.mark_task_as_complete, name='mark-task-as-complete'),

   path('U/guestlist/', wedplanner.guest_list, name='guestlist'),

   path('U/budget-manager/', wedplanner.budget_manager, name='budget-manager'),
   path('U/budget-manager/create-budget-item', wedplanner.create_budget_item),
   path('U/budget-manager/<int:budget_item_id>/update', wedplanner.update_budget_item),
   path('U/budget-manager/<int:budget_item_id>/delete', wedplanner.delete_budget_item),
   path('U/budget-manager/expenses-in-category/<int:category_id>', wedplanner.get_budget_items_in_category),

   path('U/bookmarks/', wedplanner.bookmarks, name='bookmarks'),
]


# VENDORS
urlpatterns += [

]