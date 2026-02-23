from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import logging
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny


from .serializers import STKPushSerializer
from django.http import JsonResponse
from django.utils.timezone import now
from datetime import timedelta
from django.utils import timezone
import json

from payments.models import Payment, ExternalApp
from payments.services.daraja import DarajaService
from .authentication import APIKeyAuthentication
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAPIKeyAuthenticated



logger = logging.getLogger("payments")


@csrf_exempt
def c2b_validation(request):
    """
    Safaricom sends transaction details for validation.
    Return accept or reject.
    """
    data = json.loads(request.body)

    # print("VALIDATION REQUEST:", data)
    logger.info(f"C2B VALIDATION REQUEST: {data}")


    # accept all payments for now
    return JsonResponse({
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    })


@csrf_exempt
def c2b_confirmation(request):
    """
    Safaricom sends confirmation after payment is successful.
    Save payment here.
    """
    data = json.loads(request.body)

    # print("CONFIRMATION DATA:", data)
    logger.info(f"C2B CONFIRMATION RECEIVED: {data}")


    Payment.objects.create(
        phone_number=data.get("MSISDN"),
        amount=data.get("TransAmount"),
        reference=data.get("BillRefNumber"),
        mpesa_receipt_number=data.get("TransID"),
        status="COMPLETED"
    )
    logger.info(f"PAYMENT RECORDED: Receipt={data.get('TransID')} Amount={data.get('TransAmount')}")


    return JsonResponse({"ResultCode": 0, "ResultDesc": "Success"})


class STKPushView(APIView):
    authentication_classes = [APIKeyAuthentication]
    permission_classes = [IsAPIKeyAuthenticated]

    def post(self, request):
        serializer = STKPushSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        external_app = request.user  # This is ExternalApp (from APIKeyAuthentication)

        daraja = DarajaService()

        response = daraja.stk_push(
            phone_number=data["phone_number"],
            amount=data["amount"],
            reference=data["reference"],
            description=data["description"],
        )

        # Save initial payment record
        payment = Payment.objects.create(
            external_reference=data["reference"],
            app_name=external_app.name,
            app=external_app,
            phone_number=data["phone_number"],
            amount=data["amount"],
            payment_type="STK",
            checkout_request_id=response.get("CheckoutRequestID"),
            merchant_request_id=response.get("MerchantRequestID"),
            status="PENDING",
            raw_callback=response
        )

        return Response({
            "message": "STK initiated",
            "payment_id": payment.id,
            "daraja_response": response
        }, status=status.HTTP_200_OK)



@csrf_exempt
@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
def stk_callback(request):

    data = request.data
    logger.info(f"STK Callback Received: {data}")

    try:
        stk_data = data["Body"]["stkCallback"]
        checkout_request_id = stk_data["CheckoutRequestID"]
        result_code = stk_data["ResultCode"]
        result_desc = stk_data["ResultDesc"]

        payment = Payment.objects.get(checkout_request_id=checkout_request_id)

        payment.raw_callback = data

        if result_code == 0:
            # SUCCESS
            metadata = stk_data.get("CallbackMetadata", {}).get("Item", [])

            receipt_number = None
            for item in metadata:
                if item["Name"] == "MpesaReceiptNumber":
                    receipt_number = item["Value"]

            payment.status = "SUCCESS"
            payment.mpesa_receipt_number = receipt_number

            logger.info(f"Payment SUCCESS: {receipt_number}")

        else:
            payment.status = "FAILED"
            logger.warning(f"Payment FAILED: {result_desc}")

        payment.save()

    except Payment.DoesNotExist:
        logger.error("Payment not found for CheckoutRequestID")

    except Exception as e:
        logger.error(f"Error processing STK callback: {str(e)}")

    return Response({"ResultCode": 0, "ResultDesc": "Accepted"})

class VerifyPaymentView(APIView):
    """
    Universal payment verification.

    Priority:
    1. receipt + phone (best)
    2. receipt only
    3. reference
    """

    authentication_classes = [APIKeyAuthentication]
    permission_classes = [IsAPIKeyAuthenticated]

    def get(self, request):
        app = request.user  # ExternalApp from API key

        receipt = request.GET.get("receipt")
        reference = request.GET.get("reference")
        phone = request.GET.get("phone")

        if not receipt and not reference:
            return Response(
                {"error": "Provide receipt or reference"},
                status=status.HTTP_400_BAD_REQUEST
            )

        payment = Payment.objects.filter(
            app=app,
            status="COMPLETED"
        )

        # 1️⃣ Receipt + optional phone
        if receipt:
            payment = payment.filter(mpesa_receipt_number=receipt)

            if phone:
                payment = payment.filter(phone_number=phone)

            payment = payment.first()

        # 2️⃣ Reference lookup (STK initiated payments)
        elif reference:
            payment = payment.filter(external_reference=reference).first()

        if not payment:
            return Response({"paid": False})

        return Response({
            "paid": True,
            "amount": payment.amount,
            "phone": payment.phone_number,
            "receipt": payment.mpesa_receipt_number,
            "reference": payment.reference,
            "claimed": payment.claimed,
            "date": payment.created_at,
        })

# class VerifyPaymentView(APIView):
#     """
#     Verify if a payment has been completed.

#     Supports:
#     - receipt number (highest priority)
#     - reference
#     - phone + amount (fallback)
#     """
#     authentication_classes = [APIKeyAuthentication]
#     permission_classes = [IsAPIKeyAuthenticated]

#     def get(self, request):
#         receipt = request.GET.get("receipt")
#         reference = request.GET.get("reference")
#         phone = request.GET.get("phone")
#         amount = request.GET.get("amount")

#         payment = None

#         # ✅ 1. Receipt lookup (MOST reliable)
#         if receipt:
#             payment = Payment.objects.filter(
#                 mpesa_receipt=receipt,
#                 status="COMPLETED"
#             ).first()

#         # ✅ 2. Reference lookup
#         elif reference:
#             payment = Payment.objects.filter(
#                 reference=reference,
#                 status="COMPLETED"
#             ).first()

#         # ✅ 3. Phone + Amount fallback (recent payments only)
#         elif phone and amount:
#             try:
#                 amount = float(amount)
#             except ValueError:
#                 return Response(
#                     {"error": "Invalid amount"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             recent_time = now() - timedelta(minutes=10)

#             payment = Payment.objects.filter(
#                 phone_number=phone,
#                 amount=amount,
#                 status="COMPLETED",
#                 created_at__gte=recent_time
#             ).order_by("-created_at").first()

#         else:
#             return Response(
#                 {"error": "Provide receipt, reference, or phone & amount"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         if not payment:
#             return Response({"paid": False})

#         logger.info(
#             f"PAYMENT VERIFIED: receipt={payment.mpesa_receipt} ref={payment.reference}"
#         )

#         return Response({
#             "paid": True,
#             "amount": payment.amount,
#             "phone": payment.phone_number,
#             "receipt": payment.mpesa_receipt,
#             "reference": payment.reference,
#             "claimed": payment.claimed,
#             "date": payment.created_at,
#         })
    

class ClaimPaymentView(APIView):
    """
    Mark payment as claimed after use.
    """
    authentication_classes = [APIKeyAuthentication]
    permission_classes = [IsAPIKeyAuthenticated]

    def post(self, request):
        app = request.user
        reference = request.data.get("reference")

        if not reference:
            return Response(
                {"error": "reference is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payment = Payment.objects.get(reference=reference, app=app)

            if payment.claimed:
                return Response(
                    {"message": "Payment already claimed"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            payment.claimed = True
            payment.claimed_at = timezone.now()
            payment.save()

            logger.info(f"PAYMENT CLAIMED: {reference}")

            return Response({"message": "Payment claimed successfully"})

        except Payment.DoesNotExist:
            return Response(
                {"error": "Payment not found"},
                status=status.HTTP_404_NOT_FOUND,
            )