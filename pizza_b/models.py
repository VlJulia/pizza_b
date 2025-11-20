from django.db import models

# Create your models here.

class Pizza(models.Model):
    name = models.TextField()
    type = models.TextField()
    cost = models.FloatField()
    description = models.TextField()
    # ingredients = for the future, perhaps for searching



class User(models.Model):
    phone_number = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=255)


class Branch(models.Model):
    number = models.CharField(max_length=50, unique=True)
    address = models.TextField()
    def __str__(self):
        address_part = self.address[:50] # first 40 simvolov
        return f"{self.number} - {address_part}"
    
class Driver(models.Model):
    DRIVER_STATUS = [
        ('free', 'Свободен'),
        ('busy', 'Занят'),
        ('offline', 'Не в сети'),
    ]
    
    phone_number = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=DRIVER_STATUS, default='offline')
    current_location = models.CharField(max_length=100, blank=True)
    branch = models.ForeignKey('Branch', on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)

class Order(models.Model):
    ORDER_STATUS = [
        ('pending', 'Ожидает подтверждения'),
        ('accepted', 'Принят'),
        ('preparing', 'Готовится'),
        ('assigned', 'Назначен водителю'),
        ('on_way', 'В пути'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
    ]
    
    customer_phone = models.CharField(max_length=20)
    delivery_address = models.TextField()
    delivery_coordinates = models.CharField(max_length=100, blank=True)  # tipa "56.3287,44.0020"
    total_cost = models.FloatField()
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    estimated_delivery_time = models.IntegerField(null=True)  
    
    pizzas = models.ManyToManyField(Pizza, through='OrderItem')
    driver = models.ForeignKey('Driver', on_delete=models.SET_NULL, null=True, blank=True)
    branch = models.ForeignKey('Branch', on_delete=models.SET_NULL, null=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.FloatField()