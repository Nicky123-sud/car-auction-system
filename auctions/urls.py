

from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views
from .views import process_payment, mpesa_callback, VehicleViewSet, BidViewSet, PaymentViewSet, RegisterView, LoginView, \
    mark_as_read, register_view, login_view
from .views import notifications

router = DefaultRouter()
router.register(r'vehicles', VehicleViewSet)
router.register(r'bids', BidViewSet)
router.register(r'payments', PaymentViewSet)
urlpatterns = [
    path('', views.index, name='index'),
    path('auctions/', views.auction_list, name='auction_list'),
    path('auction/<int:id>/', views.auction_detail, name='auction_detail'),
    path('bid/<int:id>/', views.bid_form, name='bid_form'),
    path('buy-now/<int:id>/', views.buy_now, name='buy_now'),
    # Use the template view for GET requests
    path('register/', views.register_view, name='register'),
    # API endpoint for registration (if needed)
    path('api/register/', RegisterView.as_view(), name='register_api'),
    path('login/', login_view, name='login'),  # Only keep this line
    path('logout/', views.logout, name='logout'),
    path('listings/', views.listings, name='listings'),
    path('listing/<int:pk>/', views.vehicle_detail, name='vehicle_detail'),
    path('create-listing/', views.create_listing, name='create_listing'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path("buy-now/<int:vehicle_id>/", views.process_buy_now, name="process_buy_now"),
    path("payment/process/", process_payment, name="process_payment"),
    path("payment/callback/", mpesa_callback, name="mpesa_callback"),
    path('search/', views.search_vehicle, name='search_vehicle'),
    path('notifications/', notifications, name='notifications'),
    path('notifications/read/<int:notification_id>/', mark_as_read, name='mark_as_read'),
]
