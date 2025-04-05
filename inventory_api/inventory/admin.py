from django.contrib import admin
from .models import Category, Product, Variant, Sale, InventoryAlert

admin.site.register([Category, Product, Variant, Sale, InventoryAlert])