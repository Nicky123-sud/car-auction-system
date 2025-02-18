import base64
import datetime
import base64
import json

import requests
from django.conf import settings
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth import authenticate
from django.utils.timezone import now

from django.shortcuts import render, redirect
from rest_framework import generics, status, viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Vehicle, Bid, Payment
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, BidSerializer, PaymentSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    BidSerializer,
    PaymentSerializer,
    VehicleSerializer
)
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Bid, Vehicle
from .serializers import BidSerializer
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Sum
from .models import Vehicle, Bid, Payment, User

from django.http import JsonResponse
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from .models import Vehicle
from .forms import ListingForm
from django.contrib.auth import get_user_model
CustomUser = get_user_model()
from django.db.models import Max, Count

# ✅ Endpoints:
#
# POST /api/register/ → User Signup
# POST /api/login/ → User Login (JWT Token)
# Create your views here.
# ✅ User Registration (Signup)
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# ✅ User Login (JWT Authentication)
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': UserSerializer(user).data
                }, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


# 🔹 CRUD for Vehicles
class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

# 🔹 Bidding System API
# ✅ Endpoints:
# GET /api/bids/ → View all bids
# POST /api/bids/ → Place a bid

class BidViewSet(viewsets.ModelViewSet):
    queryset = Bid.objects.all()
    serializer_class = BidSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)


# 🔹 Payments API
# GET /api/payments/ → View all payments
# POST /api/payments/ → Process payment

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)


# ✅ Prevents users from bidding lower than the highest bid
# ✅ Saves bids in the database
# ✅ Returns updated highest bid
@api_view(["GET"])
def get_highest_bid(request):
    vehicle_id = request.GET.get("vehicle")
    highest_bid = Bid.objects.filter(vehicle_id=vehicle_id).order_by("-amount").first()
    if highest_bid:
        return Response({"amount": highest_bid.amount})
    return Response({"amount": None})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def place_bid(request):
    """Handles bid placement logic with validation."""
    user = request.user

    try:
        vehicle = get_object_or_404(Vehicle, id=request.data["vehicle"])
        amount = float(request.data["amount"])

        # Ensure bid is greater than zero
        if amount <= 0:
            return Response({"error": "Bid amount must be greater than zero."}, status=400)

        # Fetch highest bid
        highest_bid = Bid.objects.filter(vehicle=vehicle).order_by("-amount").first()

        # Check if bid is higher than the current highest bid
        if highest_bid and amount <= highest_bid.amount:
            return Response({"error": "Bid must be higher than the current highest bid."}, status=400)

        with transaction.atomic():
            # Create a new bid
            bid = Bid.objects.create(user=user, vehicle=vehicle, amount=amount)

            # Notify the seller
            Notification.objects.create(
                user=vehicle.seller,
                title="New Bid Placed",
                message=f"A new bid of KSh {amount} has been placed on your vehicle: {vehicle.title}.",
            )

            return Response(
                {"message": "Bid placed successfully!", "amount": bid.amount, "vehicle": vehicle.title},
                status=201,
            )

    except KeyError:
        return Response({"error": "Invalid request data."}, status=400)
    except ValueError:
        return Response({"error": "Invalid bid amount."}, status=400)


# ✅ Fetches auction statistics dynamically
# ✅ Returns JSON data for frontend visualization
# @login_required
# def admin_dashboard_stats(request):
#     total_users = User.objects.count()
#     total_vehicles = Vehicle.objects.count()
#     active_auctions = Vehicle.objects.filter(status="active").count()
#     total_revenue = Payment.objects.aggregate(Sum("amount"))["amount__sum"] or 0

#     stats = {
#         "total_users": total_users,
#         "total_vehicles": total_vehicles,
#         "active_auctions": active_auctions,
#         "total_revenue": total_revenue,
#     }
    
#     return JsonResponse(stats)

# @login_required
# def seller_dashboard_stats(request):
#     seller_vehicles = Vehicle.objects.filter(seller=request.user)
#     total_listings = seller_vehicles.count()
#     sold_vehicles = seller_vehicles.filter(status="sold").count()
#     active_auctions = seller_vehicles.filter(status="active").count()

#     stats = {
#         "total_listings": total_listings,
#         "sold_vehicles": sold_vehicles,
#         "active_auctions": active_auctions,
#     }
    
#     return JsonResponse(stats)

# ✅ Allows instant purchases.
# ✅ Ends the auction immediately.


@login_required
def buy_now(request, vehicle_id):
    try:
        user = request.user
        vehicle = Vehicle.objects.get(id=vehicle_id)

        # Check if the vehicle is already sold
        if vehicle.is_sold:
            return JsonResponse({"error": "This vehicle is already sold."}, status=400)

        # Check if "Buy Now" price exists
        if not vehicle.buy_now_price:
            return JsonResponse({"error": "Buy Now option is not available for this auction."}, status=400)

        # Check if the auction has ended
        if now() > vehicle.auction_end_time:
            return JsonResponse({"error": "The auction has already ended."}, status=400)

        # Mark the vehicle as sold and finalize purchase
        vehicle.is_sold = True
        vehicle.current_price = vehicle.buy_now_price
        vehicle.save()

        return JsonResponse({"success": True, "message": "Vehicle purchased successfully!", "final_price": vehicle.buy_now_price})

    except Vehicle.DoesNotExist:
        return JsonResponse({"error": "Vehicle not found."}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)


def home(request):
    return render(request, 'auctions/home.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'auctions/login.html', {'error': 'Invalid username or password'})
        return render(request, 'login.html')
    
    
def vehicle_detail(request, vehicle_id):
    try:
        vehicle = Vehicle.objects.get(id=vehicle_id)
        
        bids = Bid.objects.filter(vehicle=vehicle)
        
        highest_bid = bids.order_by('-amount').first()
        
        return render(request,'auctions/vehicle_detail.html', {'vehicle': vehicle, 'bids': bids, 'highest_bid': highest_bid})
    except Vehicle.DoesNotExist:
        
        return render(request, 'auctions/vehicle_detail.html', {'error': 'Vehicle not found'})



@login_required
def dashboard(request):
    # Count total listings
    total_listings = Vehicle.objects.count()

    # Count active bids
    active_bids = Bid.objects.count()

    # Count total users
    total_users = CustomUser.objects.count()  # Change this to your user model

    # Revenue statistics (assuming you store final sale prices in Bid)
    total_revenue = Bid.objects.aggregate(total=Max('amount'))['total'] or 0

    # Auction statistics for chart
    auction_stats = (
        Vehicle.objects
        .values('auction_type')
        .annotate(count=Count('id'))
    )

    # Format data for frontend
    data = {
        "total_listings": total_listings,
        "active_bids": active_bids,
        "total_users": total_users,
        "total_revenue": total_revenue,
        "auction_stats": list(auction_stats),  # Convert QuerySet to list
    }

    return JsonResponse(data)


# M-pesa Credentials
MPESA_SHORTCODE = "+254757246043"
MPESA_PASSKEY = "bfb279f9aa9b8bdfd6b5e0c742417db7c2a79d1c4419eb8c1fc152cc5d49d54f"
MPESA_CONSUMER_KEY = "cCyaNg6VFQgLjwJ0QaPLML3vanNbzBLmCTODMGnaRpU20TfH"
MPESA_CONSUMER_SECRET = "onTzPOTB6fHp6ch2mgsmRRNOYEy0sD4tTMwjGXRNpQHwWpmh5gSGAY2R9BIZykOz"

# Get M-pesa OAuth Token
def get_mpesa_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=(MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET))
    return response.json()["access_token"]

# Initiate STK PUSH PAYMENT
def process_payment(request, MPESA_CALLBACK_URL=None):
    if request.method == "POST":
        phone = request.POST["phone"]
        amount = request.POST["amount"]

        #Format phone number to start with 2547
        if not phone.startswith("2547") or len(phone) != 12:
            return JsonResponse({"error": "Invalid phone number."}, status=400)

        access_token = get_mpesa_token()
        timestamp = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        password = base64.base64encode(f"{MPESA_SHORTCODE}{MPESA_PASSKEY}{timestamp}".encode().decode())

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        payload = {
            "BusinessShortCode": MPESA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": MPESA_SHORTCODE,
            "PhoneNumber": phone,
            "CallBackURL": MPESA_CALLBACK_URL,
            "AccountReference": "CarAuction",
            "TransactionDesc": "Car Auction Payment"

        }

        response = requests.post(
            "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
            json=payload,
            headers=headers
        )
        response_data = response.json()
        if response_data.get("ResponseCode") == "0":
            return JsonResponse({"message": "STK Push sent. Complete the payment on your phone."})
        else:
            return JsonResponse({"error": "STK Push failed", "details": response_data}, status=400)

    return JsonResponse({"error": "Not enough money."}, status=400)

def mpesa_callback(request):
    data = json.loads(request.body.decode("utf-8"))
    print("M-pesa Callback Data:", data)

    result_code = data.get("Body", {}).get("stkCallback", {}).get("ResultCode")


    if result_code == 0:
        return JsonResponse({"message": "Payment successful!"}, status=200)
    else:
        return JsonResponse({"error": f"Payment failed: {result_desc}"}, status=400)


from django.shortcuts import render

def index(request):
    # Your logic to render the home page or any template
    return render(request, 'auctions/index.html')  # Assuming you have an 'index.html' template
# ✅ Home Page
def home(request):
    return render(request, 'auctions/home.html')

# ✅ Listings Page
def listings(request):
    vehicles = Vehicle.objects.all()
    return render(request, 'auctions/listings.html', {'vehicles': vehicles})


def logout(request):
    return None


def search_vehicle(request):
    query = request.GET.get('q')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    year = request.GET.get('year')

    vehicles = Vehicle.objects.all()

    if query:
        vehicles = vehicles.filter(title__icontains=query) | vehicles.filter(make__icontains=query) | vehicles.filter(model__icontains=query)
    if min_price:
        vehicles = vehicles.filter(price__gte=min_price)
    if max_price:
        vehicles = vehicles.filter(price__lte=max_price)
    if year:
        vehicles = vehicles.filter(year=year)

    # Get unique years for filtering dropdown
    years = Vehicle.objects.values_list('year', flat=True).distinct().order_by('-year')

    return render(request, 'auctions/search_vehicle.html', {'vehicles': vehicles, 'years': years})



def create_listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('listings')  # Redirect to the listings page after creation
    else:
        form = ListingForm()

    return render(request, 'auctions/create_listing.html', {'form': form})


def auction_list(request):
    auctions = Vehicle.objects.all()  # Fetch all auction vehicles
    return render(request, 'auctions/listings.html', {'auctions': auctions})

def auction_detail(request, id):
    vehicle = get_object_or_404(Vehicle, pk=id)
    bids = Bid.objects.filter(vehicle=vehicle).order_('-timestamp')
    highest_bid = bids.first()

    return render(request, 'auction_detail.html', {
        'vehicle': vehicle,
        'bids': bids,
        'highest_bid': highest_bid,
    })

@login_required
def bid_form(request, id):
    vehicle = get_object_or_404(Vehicle, id=id)

    if request.method == "POST":
        form = BidForm(request.POST, vehicle=vehicle)
        if form.is_valid():
            new_bid = form.save(commit=False)
            new_bid.vehicle = vehicle
            new_bid.user = request.user
            new_bid.save()
            messages.success(request, "Your bid has been placed successfully!")
            return redirect('auction_detail', id=vehicle.id)
        else:
            messages.error(request, "Invalid bid. Please enter a valid amount.")

    return redirect('auction_detail', id=vehicle.id)


def notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'notifications.html', {'notifications': notifications})

def mark_as_read(request, notification_id):
    if request.method == "POST":
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"}, status=400)

def mark_all_as_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({"status": "success"})


@login_required
def process_buy_now(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)

    # Check if the vehicle has already been sold
    if vehicle.is_sold:
        messages.error(request, "Sorry, this vehicle has already been sold.")
        return redirect("listings")  # Redirect to listings page or any other appropriate page

    # Proceed with the purchase when the form is submitted
    if request.method == "POST":
        # Simulate the purchase process (payment gateway integration can be added here)
        vehicle.is_sold = True  # Mark the vehicle as sold after the purchase
        vehicle.save()

        # Display a success message to the user
        messages.success(request, "Congratulations! You have successfully purchased this vehicle.")

        # Redirect to the dashboard after the successful purchase
        return redirect("dashboard")

    return render(request, "buy_now.html", {"vehicle": vehicle})