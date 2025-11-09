from django.contrib import admin
from django.urls import path,include
from pizza_b.api import PizzaViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register('',PizzaViewSet)
urlpatterns = [
    path('pizzas/', include(router.urls)),
]
