from django.db import models
from django.contrib.auth.models import User
from products.models import Product


class SalesReport(models.Model):
    date = models.DateField(auto_now_add=True)
    total_sales = models.DecimalField(max_digits=15, decimal_places=2)
    orders_count = models.PositiveIntegerField()

    def __str__(self):
        return f"Sales Report - {self.date}"


class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Activity by {self.user.username} - {self.activity}"


class MostPurchasedProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    purchase_count = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.name} - Purchased {self.purchase_count} times"
