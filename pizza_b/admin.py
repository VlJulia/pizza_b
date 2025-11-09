from django.contrib import admin
from pizza_b.models import Pizza
# Register your models here.

#admin.site.register(Pizza)
@admin.register(Pizza)
class PizzaAdmin(admin.ModelAdmin):
    list_display=('name','type','cost','description')