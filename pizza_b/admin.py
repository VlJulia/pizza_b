from django.contrib import admin
from pizza_b.models import Pizza, Branch, Driver, Order
# Register your models here.
from django.contrib.auth import get_user_model
from .routing import Routing
User = get_user_model()
#admin.site.register(Pizza)
@admin.register(Pizza)
class PizzaAdmin(admin.ModelAdmin):
    list_display=('name','type','cost','description')

    
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number')

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('number', 'address')
    def save_model(self, request, obj, form, change):
        # If coordinates not set, geocode from address
        if obj.address and (not obj.coordinates or str(obj.coordinates).strip() == ""):
            result = Routing.Geocode(obj.address)
            obj.coordinates = result.strip()
        super().save_model(request, obj, form, change)
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_phone', 'status', 'total_cost', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer_phone', 'delivery_address')

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('account', 'status', 'branch')
    list_filter = ('status', 'branch')


    from django.contrib import admin

