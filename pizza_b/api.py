from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Pizza, User, Driver, Branch, Order, OrderItem
from .serializers import PizzaSerializer, UserSerializer, DriverSerializer, BranchSerializer, OrderItemSerializer, OrderSerializer

class PizzaViewSet(viewsets.ModelViewSet):
    queryset = Pizza.objects.all() #filters
    #permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = PizzaSerializer
    #@action(detail=True, methods=['post'])
    #def custom_action(self, request, pk=None):
    #    instance = self.get_object()
    #    print('aaaaaaaaaaaaaaa'+instance)
    #    # Логика кастомного действия
    #    return Response({'status': 'success'})




    
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
def perform_create(self, serializer):
    items_data = self.request.data.get('items', [])
    total_cost = sum(item['quantity'] * Pizza.objects.get(id=item['pizza']).cost 
                    for item in items_data)
    estimated_time = 30 

    order = serializer.save(
        total_cost=total_cost,
        estimated_delivery_time=estimated_time,
        status='pending'
    )
    

    for item_data in items_data:
        pizza = Pizza.objects.get(id=item_data['pizza'])
        OrderItem.objects.create(
            order=order,
            pizza=pizza,
            quantity=item_data['quantity'],
            price=pizza.cost
        )
    

    self.assign_driver(order)

def assign_driver(self, order):

    free_drivers = Driver.objects.filter(status='free', is_active=True)
    if free_drivers.exists():
        driver = free_drivers.first()
        order.driver = driver
        order.status = 'assigned'
        order.save()
        

        driver.status = 'busy'
        driver.save()