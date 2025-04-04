from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Product
from .serializers import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]  # Only logged-in users can access

    def get_queryset(self):
        return Product.objects.filter(user=self.request.user)  # Users see only their products

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)  # Auto-set owner on creation