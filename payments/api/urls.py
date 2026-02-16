from django.urls import path
from .views import STKPushView, stk_callback
from . import views

urlpatterns = [
    path("stk-push/", STKPushView.as_view(), name="stk-push"),
    path("mpesa/stk-callback/", stk_callback, name="stk-callback"),

    ### C2B
    path("mpesa/c2b/validation/", views.c2b_validation, name="c2b_validation"),
    path("mpesa/c2b/confirmation/", views.c2b_confirmation, name="c2b_confirmation"),
]
