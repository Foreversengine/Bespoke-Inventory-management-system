# inventory/urls.py
from rest_framework.routers import DefaultRouter
from .views import SaleViewSet, OrderViewSet

router = DefaultRouter()
router.register(r'sales', SaleViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = router.urls