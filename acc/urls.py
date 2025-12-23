from django.urls import path
from .views import RegisterCustomerView, RegisterDriverView, LoginView

urlpatterns = [
    path("register/customer/", RegisterCustomerView.as_view()),
    path("register/driver/", RegisterDriverView.as_view()),
    path("login/", LoginView.as_view()),
]