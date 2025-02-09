from django.contrib.auth import authenticate
from django.shortcuts import render
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
def place_bid(request):
    user = request.user
    vehicle = get_object_or_404(Vehicle, id=request.data["Vehicle"])
    amount = request.data["amount"]

    highest_bid = Bid.objects.filter(vehicle=vehicle).order_by("-amount").first()
    if highest_bid and amount <= highest_bid.amount:
        return Response({"error": "Bid must be higher than the current highest bid."}, status=400)

    bid = Bid.objects.create(user=user, vehicle=vehicle, amount=amount)
    return Response({"message": "Bid placed successfully!", "amount":bid.amount})



# ✅ Fetches auction statistics dynamically
# ✅ Returns JSON data for frontend visualization
@login_required
def admin_dashboard_stats(request):
    total_users = User.objects.count()
    total_vehicles = Vehicle.objects.count()
    active_auctions = Vehicle.objects.filter(status="active").count()
    total_revenue = Payment.objects.aggregate(Sum("amount"))["amount__sum"] or 0

    stats = {
        "total_users": total_users,
        "total_vehicles": total_vehicles,
        "active_auctions": active_auctions,
        "total_revenue": total_revenue,
    }
    
    return JsonResponse(stats)

@login_required
def seller_dashboard_stats(request):
    seller_vehicles = Vehicle.objects.filter(seller=request.user)
    total_listings = seller_vehicles.count()
    sold_vehicles = seller_vehicles.filter(status="sold").count()
    active_auctions = seller_vehicles.filter(status="active").count()

    stats = {
        "total_listings": total_listings,
        "sold_vehicles": sold_vehicles,
        "active_auctions": active_auctions,
    }
    
    return JsonResponse(stats)


