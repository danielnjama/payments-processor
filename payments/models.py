# payments/models.py

from django.db import models
import uuid
# from django.contrib.auth.models import AbstractUser
import secrets

# class User(AbstractUser):
#     phone_number = models.CharField(max_length=15, unique=True)




class ExternalApp(models.Model):
    name = models.CharField(max_length=100, unique=True)
    api_key = models.CharField(max_length=100, unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.api_key:
            self.api_key = secrets.token_hex(32)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name



class Payment(models.Model):

    PAYMENT_TYPE_CHOICES = (
        ("STK", "STK Push"),
        ("C2B", "C2B"),
    )

    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    external_reference = models.CharField(max_length=100, null=True, blank=True)
    # this links the payment to your external application

    app_name = models.CharField(max_length=100,blank=True)
    # Which app sent this payment request?

    phone_number = models.CharField(max_length=15)

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    mpesa_receipt_number = models.CharField(max_length=50, null=True, blank=True, unique=True)

    checkout_request_id = models.CharField(max_length=100, null=True, blank=True)
    merchant_request_id = models.CharField(max_length=100, null=True, blank=True)

    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPE_CHOICES,default='C2B')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")

    claimed = models.BooleanField(default=False)
    claimed_at = models.DateTimeField(null=True, blank=True)

    raw_callback = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    app = models.ForeignKey(ExternalApp, on_delete=models.CASCADE, null=True, blank=True)


    def __str__(self):
        return f"{self.phone_number} - {self.amount} - {self.status}"
