from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Pizza
from .serializers import PizzaSerializer

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