from django.test import TestCase
from inventory.models import Order

class OrderModelTest(TestCase):
    def test_required_fields(self):
        order = Order.objects.create(
            # ... required fields ...
        )
        self.assertIsNotNone(order.created_at)