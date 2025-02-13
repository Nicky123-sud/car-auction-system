from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from django.db.models import Max
from django.http import JsonResponse
# from .models import Vehicle, Bid



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
    title = models.CharField(max_length=255, default="Default Title")
    current_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    buy_now_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # For "Buy Now" Option
    is_sold = models.BooleanField(default=False)  # Track if the vehicle is sold
    
    
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
    # bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    # vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    # amount = models.DecimalField(max_digits=10, decimal_places=2)
    max_bid_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Proxy Bidding

    def __str__(self):
        return f"{self.bidder.username} - Amount: {self.bid_amount} on {self.vehicle}"

    def __str__(self):
        return f"{self.bidder} - {self.vehicle.title} - {self.amount}"

# ✅ Stores max bid amount for proxy bidding.
# ✅ Adds "Buy Now" price to vehicles.
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
    
    
    
    
def place_bid(request, vehicle_id):
    user = request.user
    amount = float(request.POST.get("amount"))
    max_bid_amount = float(request.POST.get("max_bid_amount", amount))  # Default to normal bid if not set

    vehicle = Vehicle.objects.get(id=vehicle_id)

    if now() > vehicle.auction_end_time:
        return JsonResponse({"error": "Auction has ended."}, status=400)

    # Get the current highest bid
    highest_bid = Bid.objects.filter(vehicle=vehicle).aggregate(Max("amount"))["amount__max"] or vehicle.current_price

    if amount < highest_bid:
        return JsonResponse({"error": "Bid must be higher than the current highest bid."}, status=400)

    # Place the bid
    bid = Bid.objects.create(bidder=user, vehicle=vehicle, amount=amount, max_bid_amount=max_bid_amount)

    # Automatically bid up to max_bid_amount
    competing_bids = Bid.objects.filter(vehicle=vehicle).exclude(bidder=user).order_by("-max_bid_amount")

    if competing_bids.exists():
        top_competing_bid = competing_bids.first()
        new_auto_bid = min(top_competing_bid.max_bid_amount + 1, max_bid_amount)
        if new_auto_bid > highest_bid:
            Bid.objects.create(bidder=user, vehicle=vehicle, amount=new_auto_bid)

    # Update vehicle price
    vehicle.current_price = Bid.objects.filter(vehicle=vehicle).aggregate(Max("amount"))["amount__max"]
    vehicle.save()

    return JsonResponse({"success": "Bid placed successfully!", "new_price": vehicle.current_price})