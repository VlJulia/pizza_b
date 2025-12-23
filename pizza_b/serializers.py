from rest_framework import serializers
from rest_framework.authtoken.models import Token
from .models import Pizza, Branch, Driver, Order, OrderItem

from .models import Driver, Branch


from django.contrib.auth import get_user_model
User = get_user_model()


Account = get_user_model()


class PizzaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pizza
        fields = '__all__'
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'    


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = '__all__'




class DriverSerializer(serializers.ModelSerializer):
    # account fields provided in the same payload
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=4)
    name = serializers.CharField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)

    branch_id = serializers.PrimaryKeyRelatedField(
        queryset=Branch.objects.all(),
        source="branch",
        write_only=True,
        required=False,
        allow_null=True,
    )

    # read-only extras
    branch = serializers.StringRelatedField(read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Driver
        fields = [
            "id",
            # account inputs
            "username", "password", "name", "phone_number",
            # driver fields
            "status", "coordinates", "branch", "branch_id", "is_active",
            # extras
            "status_display", "token",
        ]
        read_only_fields = ["id", "status_display", "token", "branch"]

    def get_token(self, obj):
        token, _ = Token.objects.get_or_create(user=obj.account)
        return token.key

    def create(self, validated_data):
        username = validated_data.pop("username")
        password = validated_data.pop("password")
        name = validated_data.pop("name", "")
        phone_number = validated_data.pop("phone_number", "")

        # create auth user
        account = Account.objects.create_user(
            username=username,
            password=password,
        )
        # if your Account model has these fields, set them:
        if hasattr(account, "name"):
            account.name = name
        if hasattr(account, "phone_number"):
            account.phone_number = phone_number
        account.save()

        # create driver profile
        driver = Driver.objects.create(account=account, **validated_data)

        # ensure token exists (optional; serializer also returns it)
        Token.objects.get_or_create(user=account)

        return driver


class OrderItemSerializer(serializers.ModelSerializer):
    pizza_name = serializers.CharField(source='pizza.name', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['pizza', 'pizza_name', 'quantity', 'price']
        read_only_fields = ['price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, source='orderitem_set')
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    total_cost = serializers.SerializerMethodField()

    driver_name = serializers.CharField(source='driver.name', read_only=True)
    branch_address = serializers.CharField(source='branch.address', read_only=True)  
    user_name = serializers.CharField(source='user.name', read_only=True)
    class Meta:
        model = Order
        fields = [
            'id', 'customer_phone', 'delivery_address', 'delivery_coordinates',
            'total_cost', 'status', 'status_display', 'estimated_delivery_time',
            'created_at', 'updated_at', 'driver', 'branch', 'items', 'user_name', 'branch_address', 'driver_name',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'status_display']
    def create(self, validated_data):
        items_data = validated_data.pop('orderitem_set', [])
        
        total_cost = 0
        for item_data in items_data:
            pizza = item_data['pizza']
            quantity = item_data.get('quantity', 1)
            total_cost += pizza.cost * quantity
        
        validated_data['total_cost'] = total_cost
        
        order = Order.objects.create(**validated_data)
        
        for item_data in items_data:
            OrderItem.objects.create(
                order=order,
                pizza=item_data['pizza'],
                quantity=item_data.get('quantity', 1),
                price=item_data['pizza'].cost
            )
        
        return order
    def get_total_cost(self, obj):
        return sum(item.quantity * item.price for item in obj.orderitem_set.all())