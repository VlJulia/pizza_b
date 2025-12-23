from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from pizza_b.models import Driver
from .serializers import LoginSerializer, RegisterCustomerSerializer, RegisterDriverSerializer

Account = get_user_model()

class LoginView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        data = s.validated_data

        user = authenticate(username=data["username"], password=data["password"])
        if not user:
            return Response({"error": "Invalid credentials"}, status=400)

        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})

class RegisterCustomerView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterCustomerSerializer

    def post(self, request, *args, **kwargs):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        data = s.validated_data

        if Account.objects.filter(username=data["username"]).exists():
            return Response({"error": "username already exists"}, status=400)

        user = Account.objects.create_user(username=data["username"], password=data["password"])
        if hasattr(user, "name"):
            user.name = data.get("name", "")
        if hasattr(user, "phone_number"):
            user.phone_number = data.get("phone_number", "")
        user.save()

        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "account_id": user.id}, status=status.HTTP_201_CREATED)

class RegisterDriverView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterDriverSerializer

    def post(self, request, *args, **kwargs):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        data = s.validated_data

        if Account.objects.filter(username=data["username"]).exists():
            return Response({"error": "username already exists"}, status=400)

        user = Account.objects.create_user(username=data["username"], password=data["password"])
        if hasattr(user, "name"):
            user.name = data.get("name", "")
        if hasattr(user, "phone_number"):
            user.phone_number = data.get("phone_number", "")
        user.save()

        driver = Driver.objects.create(account=user, branch_id=data["branch_id"])
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {"token": token.key, "driver_id": driver.id, "account_id": user.id},
            status=status.HTTP_201_CREATED,
        )