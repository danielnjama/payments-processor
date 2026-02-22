from django.contrib import admin
from .models import Payment, ExternalApp


@admin.register(ExternalApp)
class ExternalAppAdmin(admin.ModelAdmin):
    list_display = ("name", "api_key", "is_active", "created_at")
    readonly_fields = ("api_key", "created_at")
    search_fields = ("name",)
    list_filter = ("is_active", "created_at")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
       "mpesa_receipt_number",
        "external_reference",
        "app_name",
        "phone_number",
        "amount",
        "status",
        "claimed",
        "created_at",
    )

    list_filter = ("status", "claimed", "payment_type", "created_at")
    search_fields = (
        "external_reference",
        "phone_number",
        "mpesa_receipt_number",
        "checkout_request_id",
    )

    readonly_fields = (
        "mpesa_receipt_number",
        "checkout_request_id",
        "merchant_request_id",
        "raw_callback",
        "created_at",
    )

    ordering = ("-created_at",)
