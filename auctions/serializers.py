from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Vehicle, Bid, Payment, User


# User Serializer (For Registration & Authentication) ✅ Handles:
#
# User registration
# Login authentication
user = get_user_model()
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = user
        fields = ['id', 'username', 'email', 'phone_number', 'user_type']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = user
        fields = ['id', 'username', 'email', 'phone_number', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            phone_number=validated_data['phone_number'],
            password=validated_data['password'],
            user_type=validated_data['user_type']
        )
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


# Vehicle Serializer
# ✅ Handles:
# Vehicle CRUD operations

class VehicleSerializer(serializers.ModelSerializer):
    seller = UserSerializer(read_only=True)

    class Meta:
        fields = '__all__'



# Bid Serializer
# ✅ Handles:
# 
# Bidding system
class BidSerializer(serializers.ModelSerializer):
    bidder = UserSerializer(read_only=True)

    class Meta:
        model = Bid
        fields = '__all__'
        
        
# Payment Serializer
# ✅ Handles:
#
# Payments processing
class PaymentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'





