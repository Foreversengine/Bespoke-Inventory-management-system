from rest_framework import serializers
from .models import InventoryItem
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class InventoryItemSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = InventoryItem
        fields = '__all__'
        read_only_fields = ['date_added', 'last_updated']