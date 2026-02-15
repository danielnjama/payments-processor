from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import logging
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from payments.models import Payment
from payments.services.daraja import DarajaService
from payments.models import Payment
from .serializers import STKPushSerializer


logger = logging.getLogger("payments")



class STKPushView(APIView):

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
