from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class User(AbstractUser):
    USER_TYPES = (
        ('buyer', 'Buyer'),
        ('seller', 'Seller')
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='buyer')
    phone_number = models.CharField(max_length=15, unique=True)
    address = models.TextField(max_length=255, blank=True, null=True)

    groups = models.ManyToManyField("auth.Group", related_name="custom_user_set", blank=True)
    user_permissions = models.ManyToManyField("auth.Permission", related_name="custom_user_permissions_set", blank=True)
    def __str__(self):
        return f"{self.username} ({self.user_type})"


# Vehicle Model
class Vehicle(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicles')
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    mileage = models.PositiveIntegerField(default=0)
    starting_price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='vehicles_images/', null=True, blank=True)
    auction_end_time = models.DateTimeField()
    description = models.TextField()
    
    status = models.CharField(
        max_length=20,
        choices=[("active", "Active"), ("sold", "Sold"), ("expired", "Expired")],
        default="active",
    )

    def __str__(self):
        return f"{self.make} {self.model} ({self.year}) - Seller: {self.seller.username}"

# Bid Model

class Bid(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='bids')
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    bid_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bidder.username} - Amount: {self.bid_amount} on {self.vehicle}"


# After an auction ends the winning bidder must make a payment

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=10, choices=[('pending','pending'), ('completed', 'completed')], default='pending')
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment of {self.amount} for {self.vehicle} - {self.payment_status}"