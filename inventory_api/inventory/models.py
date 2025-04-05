from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

class Category(models.Model):
    """Product categories (e.g., Shoes, Shirts)"""
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

class Product(models.Model):
    """Base products with category and price"""
    name = models.CharField(max_length=100)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    
    def __str__(self):
        return f"{self.name} ({self.category})"

    class Meta:
        ordering = ['name']

class Variant(models.Model):
    """Product variants with size/color options"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants'
    )
    variant_name = models.CharField(max_length=100)
    size = models.CharField(max_length=10, blank=True, null=True)
    color = models.CharField(max_length=20)
    stock_quantity = models.IntegerField(default=0)
    reorder_threshold = models.IntegerField(default=5)
    sku = models.CharField(max_length=50, unique=True, editable=False)

    def clean(self):
        """Validate stock and threshold values"""
        if self.stock_quantity < 0:
            raise ValidationError("Stock quantity cannot be negative")
        if self.reorder_threshold < 0:
            raise ValidationError("Reorder threshold cannot be negative")

    def save(self, *args, **kwargs):
        """Auto-generate SKU on creation"""
        if not self.sku:
            size_part = f"-{self.size}" if self.size else ""
            self.sku = (
                f"{self.product.category.name[:3].upper()}-"
                f"{self.product.id}{size_part}-"
                f"{self.color[:3].upper()}"
            )
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.variant_name} ({self.sku})"

    class Meta:
        unique_together = [['product', 'variant_name']]
        ordering = ['product__name', 'variant_name']

class Sale(models.Model):
    """Track sales transactions"""
    variant = models.ForeignKey(
        Variant,
        on_delete=models.PROTECT,
        related_name='sales'
    )
    quantity_sold = models.PositiveIntegerField()
    sale_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False
    )

    def save(self, *args, **kwargs):
        """Auto-calculate total price"""
        self.total_price = self.variant.product.price * self.quantity_sold
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sale #{self.id} - {self.variant.sku}"

    class Meta:
        ordering = ['-sale_date']

class Order(models.Model):
    """Bespoke/custom orders"""
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='orders'
    )
    customer_name = models.CharField(max_length=100)
    design_specs = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled')
        ],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.product.name}"

    class Meta:
        ordering = ['-created_at']

class InventoryAlert(models.Model):
    """Low stock notifications"""
    variant = models.ForeignKey(
        Variant,
        on_delete=models.CASCADE,
        related_name='alerts'
    )
    alert_message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Alert for {self.variant.sku}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Stock Alert"