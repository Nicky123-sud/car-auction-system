from django.contrib import admin
from .models import User, Vehicle, Bid, Payment
# Register your models here.

admin.site.register(User)
admin.site.register(Vehicle)
admin.site.register(Bid)
admin.site.register(Payment)
