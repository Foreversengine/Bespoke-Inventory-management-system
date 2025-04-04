# inventory_api/urls.py
from django.urls import path, include

urlpatterns = [
    path('api/', include('inventory.urls')),
    path('api/auth/', include('rest_framework.urls')),
]