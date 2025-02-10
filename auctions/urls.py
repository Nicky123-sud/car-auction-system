from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, LoginView, VehicleViewSet, BidViewSet, PaymentViewSet
from django.urls import path
from .views import admin_dashboard_stats, seller_dashboard_stats
from .views import place_bid, buy_now

router = DefaultRouter()
router.register(r'vehicles', VehicleViewSet)
router.register(r'bids', BidViewSet)
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('', include(router.urls)),
    path("admin/dashboard-stats/", admin_dashboard_stats, name="admin-dashboard"),
    path("seller/dashboard-stats/", seller_dashboard_stats, name="seller-dashboard"),
]


from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, LoginView, VehicleViewSet, BidViewSet, PaymentViewSet
from .views import admin_dashboard_stats, seller_dashboard_stats

router = DefaultRouter()
router.register(r'vehicles', VehicleViewSet)
router.register(r'bids', BidViewSet)
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('', include(router.urls)),
    path("admin-dashboard/", admin_dashboard_stats, name="admin-dashboard"),
    path("seller-dashboard/", seller_dashboard_stats, name="seller-dashboard"),
    path("bid/<int:vehicle_id>/", place_bid, name="place-bid"),
    path("buy-now/<int:vehicle_id>/", buy_now, name="buy-now"),
]






