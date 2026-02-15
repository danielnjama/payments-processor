from django.urls import path
from .views import STKPushView, stk_callback

urlpatterns = [
    path("stk-push/", STKPushView.as_view(), name="stk-push"),
    path("mpesa/stk-callback/", stk_callback, name="stk-callback"),
]
