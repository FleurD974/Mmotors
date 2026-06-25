from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404

from store.models import Application, Car

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **kwargs):
        if not email:
            raise ValueError("L'adresse email est obligatoire.")
        
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, email, password, **kwargs):
        kwargs["is_staff"] = True
        kwargs["is_superuser"] = True
        kwargs["is_active"] = True
        
        return self.create_user(email=email, password=password, **kwargs)

class Customer(AbstractUser):
    """"Class to handle customer"""
    username = None
    email = models.EmailField(max_length=240, unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def create_application(self, slug):
        car = get_object_or_404(Car, slug=slug)
        application, created = Application.objects.get_or_create(customer=self, car=car)

        if application.status != 'draft':
            return HttpResponseForbidden("Deja soumise")
        
        return application
