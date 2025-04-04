from django.db import models
from django.contrib.auth.models import User  # Add this for user ownership
from django.core.validators import MinValueValidator


class InventoryItem(models.Model):
    CATEGORY_CHOICES = [
        ('SHOES', 'Shoes'),
        ('SHIRTS', 'Shirts'),
        ('BELTS', 'Belts'),
        ('COLLARS', 'Collars'),
        ('TROUSERS', 'Trousers'),
        ('SLIPPERS', 'Slippers'),
        ('WALLETS', 'Wallets'),
    ]
    
    # Ownership: Link items to users (critical for permissions)
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='inventory_items'
    )
    
    # Required Fields (enforced at DB level)
    name = models.CharField(max_length=100, blank=False)  # No empty names
    description = models.TextField(blank=True, null=True)
    
    # Numeric Fields with Validation
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]  # Price must be > 0
    )
    
    # Category with Choices (now includes your wallet addition)
    category = models.CharField(
        max_length=20, 
        choices=CATEGORY_CHOICES,
        blank=False  # Category must be specified
    )
    
    # Auto-Timestamps (unchanged)
    date_added = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.category})"  # More descriptive

    class Meta:
        ordering = ['-date_added']  # Newest items first by default
        verbose_name_plural = "Inventory Items"  # Fix admin panel display