from django.urls import path
from . import views
from . views import STKPushView

urlpatterns = [
    # 🔹 STK Push
    path("stk-push/", STKPushView.as_view(), name="stk-push"),

    # 🔹 STK Callback (Daraja)
    path("mpesa/stk-callback/", views.stk_callback, name="stk-callback"),

    # 🔹 C2B Endpoints (Daraja)
    path("mpesa/c2b/validation/", views.c2b_validation, name="c2b-validation"),
    path("mpesa/c2b/confirmation/", views.c2b_confirmation, name="c2b-confirmation"),

    # 🔹 Payment Verification
    path("payments/verify/", views.VerifyPaymentView.as_view(), name="verify-payment"),

    # 🔹 Claim Payment
    path("payments/claim/", views.ClaimPaymentView.as_view(), name="claim-payment"),
]
