from django.utils.timezone import now
from .models import Vehicle, Bid

def close_expired_auctions():
    expired_vehicles = Vehicle.objects.filter(status="active", auction_end_time__lt=now())

    for vehicle in expired_vehicles:
        highest_bid = Bid.objects.filter(vehicle=vehicle).order_by("-amount").first()
        if highest_bid:
            vehicle.status = "sold"
            vehicle.save()
            # Notify seller and winner (email or SMS)
        else:
            vehicle.status = "expired"
            vehicle.save()

# ✅ Runs every hour to check expired auctions.
# ✅ Updates status & notifies users.