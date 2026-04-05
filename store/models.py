from django.db import models

class Car(models.Model):
    brand = models.CharField(max_length=128)
    model = models.CharField(max_length=128)
    engine = models.CharField(max_length=55)
    mileage = models.IntegerField(default=0)
    passenger_number = models.IntegerField(default=2)
    is_purchased = models.BooleanField(default=False)
    is_leased = models.BooleanField(default=True)
    purchase_price = models.FloatField(default=0.0)
    leasing_price = models.FloatField(default=0.0)
    registration_number = models.CharField(max_length=10)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.model} ({self.brand})"
    