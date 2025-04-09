from django.contrib import admin
from .models import *

@admin.register(Category, Product, Variant, Sale, Order, InventoryAudit)
class InventoryAdmin(admin.ModelAdmin):
    pass