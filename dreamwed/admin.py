from django.contrib import admin
from .models import User, WeddingPlanner, Vendor, Todo, Bookmark, Guest, BudgetItem, Review, VendorCategory


admin.site.register(User)
admin.site.register(WeddingPlanner)
admin.site.register(Vendor)
admin.site.register(Todo)
# admin.site.register(Bookmark)
# admin.site.register(Guest)
# admin.site.register(BudgetItem)
# admin.site.register(Review)
admin.site.register(VendorCategory)

# @admin.register(User)
# class UserAdmin(admin.ModelAdmin):
#    fields = ['first_name', 'last_name', 'email']
#    list_display = ['last_name', 'first_name', 'email']


# @admin.register(Vendor)
# class VendorAdmin(admin.ModelAdmin):
#    fields = ['business_name', 'category', 'city', 'location']


# @admin.register(WeddingPlanner)
# class WeddingPlannerAdmin(admin.ModelAdmin):
#    fields = ['user']




