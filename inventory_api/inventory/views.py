from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from .serializers import SignupSerializer
from .models import Category, Product, Variant, InventoryAudit, Sale, Order
from .serializers import (
    CategorySerializer, ProductSerializer, VariantSerializer,
    InventoryAuditSerializer, SaleSerializer, OrderSerializer
)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class VariantViewSet(viewsets.ModelViewSet):
    serializer_class = VariantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        product_id = self.request.query_params.get('product_id')
        if product_id:
            return Variant.objects.filter(product_id=product_id)
        return Variant.objects.filter(product__user=self.request.user)

    def perform_create(self, serializer):
        variant = serializer.save()
        variant.last_updated_by = self.request.user
        variant.save()

    @action(detail=True, methods=['post'])
    def adjust_stock(self, request, pk=None):
        variant = self.get_object()
        adjustment = request.data.get('adjustment', 0)
        reason = request.data.get('reason', 'Manual adjustment')
        
        try:
            adjustment = int(adjustment)
        except ValueError:
            return Response({'error': 'Adjustment must be an integer'}, status=status.HTTP_400_BAD_REQUEST)
        
        variant.stock_quantity += adjustment
        variant.last_updated_by = request.user
        variant.save()
        
        return Response(VariantSerializer(variant).data)

class InventoryAuditViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InventoryAuditSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        variant_id = self.request.query_params.get('variant_id')
        if variant_id:
            return InventoryAudit.objects.filter(variant_id=variant_id)
        return InventoryAudit.objects.filter(variant__product__user=self.request.user)

class SaleViewSet(viewsets.ModelViewSet):
    serializer_class = SaleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Sale.objects.filter(sold_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(sold_by=self.request.user)

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        status = self.request.query_params.get('status')
        queryset = Order.objects.filter(created_by=self.request.user)
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Order.STATUS_CHOICES):
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = new_status
        order.save()
        return Response(OrderSerializer(order).data)
    
class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = [permissions.AllowAny]  # Allow anyone to sign up

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "message": "User created successfully",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            }
        })