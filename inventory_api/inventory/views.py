from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import InventoryItem, InventoryChangeLog
from .serializers import InventoryItemSerializer, InventoryChangeLogSerializer
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import F, ExpressionWrapper, DecimalField
from django.db import transaction
from django.contrib.auth import get_user_model

User = get_user_model()

class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'quantity', 'date_added']
    ordering = ['-date_added']

    def get_queryset(self):
        queryset = super().get_queryset().filter(user=self.request.user)
        
        # Low stock filter
        low_stock = self.request.query_params.get('low_stock')
        if low_stock is not None:
            try:
                threshold = int(low_stock)
                queryset = queryset.filter(quantity__lt=threshold)
            except ValueError:
                pass
        
        # Price range filter
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price is not None:
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except ValueError:
                pass
        if max_price is not None:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except ValueError:
                pass
        
        # Calculate total value if requested
        if self.request.query_params.get('with_total_value', '').lower() in ('true', '1', 'yes'):
            queryset = queryset.annotate(
                total_value=ExpressionWrapper(
                    F('price') * F('quantity'),
                    output_field=DecimalField()
                )
            )
        
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        instance = self.get_object()
        old_quantity = instance.quantity
        
        super().perform_update(serializer)
        
        new_quantity = serializer.instance.quantity
        if old_quantity != new_quantity:
            InventoryChangeLog.objects.create(
                item=serializer.instance,
                user=self.request.user,
                previous_quantity=old_quantity,
                new_quantity=new_quantity,
                reason=f"Manual update via API (ID: {serializer.instance.id})"
            )

    @action(detail=True, methods=['post'])
    def adjust_stock(self, request, pk=None):
        item = self.get_object()
        adjustment = request.data.get('adjustment')
        reason = request.data.get('reason', 'Stock adjustment')
        
        if adjustment is None:
            return Response(
                {'error': 'Adjustment value is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            adjustment = int(adjustment)
        except (TypeError, ValueError):
            return Response(
                {'error': 'Adjustment must be an integer'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            old_quantity = item.quantity
            new_quantity = old_quantity + adjustment
            
            if new_quantity < 0:
                return Response(
                    {'error': 'Cannot have negative stock'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            item.quantity = new_quantity
            item.save()
            
            InventoryChangeLog.objects.create(
                item=item,
                user=request.user,
                previous_quantity=old_quantity,
                new_quantity=new_quantity,
                reason=reason
            )
        
        serializer = self.get_serializer(item)
        return Response(serializer.data)

    @action(detail=False)
    def low_stock(self, request):
        threshold = request.query_params.get('threshold', '5')
        try:
            threshold = int(threshold)
        except ValueError:
            threshold = 5
            
        queryset = self.filter_queryset(self.get_queryset().filter(quantity__lt=threshold))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def inventory_summary(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        
        summary = {
            'total_items': queryset.count(),
            'total_quantity': sum(item.quantity for item in queryset),
            'total_value': sum(float(item.price) * item.quantity for item in queryset),
            'categories': {
                category: queryset.filter(category=category).count()
                for category in dict(InventoryItem.CATEGORY_CHOICES).keys()
            }
        }
        
        return Response(summary)

    @action(detail=True)
    def change_history(self, request, pk=None):
        item = self.get_object()
        changes = InventoryChangeLog.objects.filter(item=item).order_by('-changed_at')
        page = self.paginate_queryset(changes)
        if page is not None:
            serializer = InventoryChangeLogSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = InventoryChangeLogSerializer(changes, many=True)
        return Response(serializer.data)