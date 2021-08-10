from django.urls import path
from dreamwed.views import dreamwed, wedplanner, vendor


# GENERAL
urlpatterns = [
   path('', dreamwed.home, name='home'),
   path('U/<int:user_id>/', dreamwed.user_profile, name='user-profile'),
   path('U/<int:user_id>/profile/', dreamwed.user_profile, name='user-profile'),
]


# WEDDING PLANNERS
urlpatterns += [
   path('vendors/', wedplanner.vendors, name='vendors'),
   path('vendors/<int:user_id>/details', wedplanner.vendor_details, name='vendor-details'),
   path('U/<int:user_id>/checklist/', wedplanner.check_list, name='checklist'),
   path('U/<int:user_id>/checklist/<int:task_id>/delete', wedplanner.delete_task, name='delete-task'),
   path('U/<int:user_id>/checklist/<int:task_id>/update', wedplanner.update_task, name='update-task'),
   path('U/<int:user_id>/checklist/<int:task_id>/mark-complete', wedplanner.mark_task_as_complete, name='mark-task-as-complete'),

   path('U/<int:user_id>/guestlist/', wedplanner.guest_list, name='guestlist'),
   path('U/<int:user_id>/budget-manager/', wedplanner.budget_manager, name='budget-manager'),
   path('U/<int:user_id>/bookmarks/', wedplanner.bookmarks, name='bookmarks'),
   path('U/<int:user_id>/create-task/', wedplanner.create_task, name='create-task'),
]


# VENDORS
urlpatterns += [

]