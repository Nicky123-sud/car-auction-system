class BuyNowTestCase(TestCase):
    def setUp(self):
        self.buyer = User.objects.create_user(username="buyer", password="testpass")
        self.seller = User.objects.create_user(username="seller", password="testpass")
        
        self.vehicle = Vehicle.objects.create(
            seller=self.seller,
            title="Honda Civic",
            description="Sport Edition",
            current_price=450000,
            buy_now_price=600000,
            auction_end_time=now() + timedelta(days=1)
        )

    def test_buy_now(self):
        self.client.login(username="buyer", password="testpass")
        response = self.client.post(f"/api/buy-now/{self.vehicle.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("success", response.json())

        updated_vehicle = Vehicle.objects.get(id=self.vehicle.id)
        self.assertEqual(updated_vehicle.status, "sold")
