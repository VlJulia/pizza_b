from django.contrib import admin
from pizza_b.models import Pizza, User, Branch, Driver, Order
# Register your models here.

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

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_phone', 'status', 'total_cost', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer_phone', 'delivery_address')

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'status', 'branch')
    list_filter = ('status', 'branch')