from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, LoginView, VehicleViewSet, BidViewSet, PaymentViewSet

router = DefaultRouter()
router.register(r'vehicles', VehicleViewSet)
router.register(r'bids', BidViewSet)
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('', include(router.urls)),
]
