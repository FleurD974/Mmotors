import uuid

from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from shop.settings import AUTH_USER_MODEL

class Car(models.Model):
    brand = models.CharField(max_length=128)
    model = models.CharField(max_length=128)
    engine = models.CharField(max_length=55)
    mileage = models.IntegerField(default=0)
    passenger_number = models.IntegerField(default=2)
    is_purchased = models.BooleanField(default=False)
    is_leased = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)
    purchase_price = models.FloatField(default=0.0)
    leasing_price = models.FloatField(default=0.0)
    registration_number = models.CharField(max_length=10)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=128, blank=True)
    
    def __str__(self):
        return f"{self.model} ({self.brand})"

    def get_absolute_url(self):
        return reverse("car", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        self.slug = self.slug or slugify(self.registration_number)
        super().save(*args, **kwargs)

class Application(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('submitted', 'Soumis'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
    ]

    customer = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Dossier {self.customer} - {self.car}"


def upload_to(instance, filename):
    ext = filename.split('.')[-1]
    new_name = f"{uuid.uuid4()}.{ext}"
    return f"applications/{instance.application_id}/{new_name}"

class DocumentType(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.name}"

class Document(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(upload_to=upload_to)
    type = models.ForeignKey(DocumentType, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Document {self.application}"
    