from django.test import TestCase
from django.contrib.auth.models import User
from django.utils.timezone import now, timedelta
from auctions.models import Vehicle, Bid

class BiddingTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="buyer1", password="testpass")
        self.user2 = User.objects.create_user(username="buyer2", password="testpass")
        self.seller = User.objects.create_user(username="seller", password="testpass")
        
        self.vehicle = Vehicle.objects.create(
            seller=self.seller,
            title="Toyota Corolla",
            description="A great car",
            current_price=500000,
            buy_now_price=700000,
            auction_end_time=now() + timedelta(days=1)
        )

    def test_place_bid(self):
        self.client.login(username="buyer1", password="testpass")
        response = self.client.post(f"/api/bid/{self.vehicle.id}/", {"amount": 510000})
        self.assertEqual(response.status_code, 200)
        self.assertIn("success", response.json())

    def test_proxy_bidding(self):
        self.client.login(username="buyer1", password="testpass")
        self.client.post(f"/api/bid/{self.vehicle.id}/", {"amount": 510000, "max_bid_amount": 600000})
        
        self.client.login(username="buyer2", password="testpass")
        response = self.client.post(f"/api/bid/{self.vehicle.id}/", {"amount": 520000})
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("success", response.json())
