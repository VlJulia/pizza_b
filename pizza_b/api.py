from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Pizza, User, Driver, Branch, Order, OrderItem
from .serializers import PizzaSerializer, UserSerializer, DriverSerializer, BranchSerializer, OrderItemSerializer, OrderSerializer
from .routing import Routing
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
    def perform_create(self, serializer):
        """
        Автоматическое геокодирование адреса филиала при создании,
        если координаты не предоставлены.
        """
        address = self.request.data.get('address', '')
        coordinates = self.request.data.get('coordinates', '')
        if not coordinates and address:
            coordinates = Routing.Geocode(address)
            if not coordinates:
                print(f"Не удалось геокодировать адрес: {address}")
        
        serializer.save(coordinates=coordinates)

class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    @action(detail=True, methods=['post'])
    def update_location(self, request, pk=None):
        """Эндпоинт для обновления местоположения водителя"""
        driver = self.get_object()
        coordinates = request.data.get('coordinates') # Формат: "55.753676,37.619899"
        if coordinates:
            driver.coordinates = coordinates
            driver.save()
            return Response({'status': 'location updated'})
        return Response({'error': 'coordinates required'}, status=400)

class OrderViewSet(viewsets.ModelViewSet):
    """
    Пример запроса:
    {
  "user":1,
  "delivery_address": "нижний новгород радужная 2",
  "customer_phone":88500508,
  "items": [
    {
      "pizza": 6,
      "quantity": 9
    }
  ]
}
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def perform_create(self, serializer):
        delivery_address = self.request.data.get('delivery_address')
        delivery_coordinates = self.request.data.get('delivery_coordinates', '')
        
        if delivery_address and not delivery_coordinates:
            found_coordinates = Routing.Geocode(delivery_address)
        else:
            found_coordinates = delivery_coordinates
        items_data = self.request.data.get('items', [])
        estimated_time = 30 

        order = serializer.save(
            delivery_coordinates = found_coordinates,
            estimated_delivery_time=estimated_time,
            status='pending'
        )
        
        self.assign_branch(order)
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
    def assign_branch(self, order):
        """Находит ближайший филиал по времени пути.""" #TODO:  FIX
        if not order.delivery_coordinates:
            return None

        nearest_branch = None
        min_time = float('inf')

        for branch in Branch.objects.all():
            route_data = Routing.GetRoute(branch.coordinates, order.delivery_coordinates)
            
            if not route_data or 'duration' not in route_data:
                continue
                
            try:
                total_duration = route_data.get('duration')
                if total_duration < min_time:
                    min_time = total_duration
                    nearest_branch = branch
                    
            except (KeyError, IndexError):
                continue

        if nearest_branch:
            order.branch = nearest_branch
            order.estimated_delivery_time = (min_time // 60) + 20
            order.save()
        else:
            all_branches = list(Branch.objects.all())
            branch_index = order.id % len(all_branches) if order.id else 0
            order.branch = all_branches[branch_index]
            order.estimated_delivery_time = 60
            order.save()

    def get_route(self, order):
        destination = order.delivery_coordinates
        current_location = any
        # Return shop if no driver assigned
        if not getattr(order, 'driver', None):
            current_location = order.branch.coordinates
        else: 
            current_location = order.driver.coordinates
        route = Routing.GetRoute(current_location, destination)
        return route
    @action(detail=True, methods=['get'], url_path='route-info')
    def get_order_route(self, request, pk=None):
        """
        Публичный API: Получить маршрут для конкретного заказа.
        Возвращает дистанцию, время и ломаную линию
         """
        order = self.get_object()
        route_data = self.get_route(order)
    
        if not route_data:
            return Response({
               'error': f'Не удалось построить маршрут для заказа {order.id}'
            }, status=400)
    

        return Response(route_data)
        