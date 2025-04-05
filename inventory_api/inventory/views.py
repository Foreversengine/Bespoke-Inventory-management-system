# inventory/views.py
from rest_framework import viewsets
from .models import Sale, Order
from .serializers import SaleSerializer, OrderSerializer

class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer