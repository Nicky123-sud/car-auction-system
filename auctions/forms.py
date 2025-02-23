from django import forms
from .models import Listing
from .models import Bid
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


CustomUser = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email")


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'make', 'model', 'year', 'mileage', 'starting_price', 'description', 'image']



class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']
        labels = {'amount': 'Bid Amount (KSh)'}
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your bid amount',
                'min': '1',
                'required': True
            })
        }

    def __init__(self, *args, **kwargs):
        self.vehicle = kwargs.pop('vehicle', None)
        super().__init__(*args, **kwargs)

    def clean_amount(self):
        """Ensure bid amount is greater than the current highest bid."""
        amount = self.cleaned_data.get('amount')

        # Get the highest bid for this vehicle
        highest_bid = Bid.objects.filter(vehicle=self.vehicle).order_by('-amount').first()
        if highest_bid and amount <= highest_bid.amount:
            raise forms.ValidationError("Your bid must be higher than the current highest bid.")

        return amount

