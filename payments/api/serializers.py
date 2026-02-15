from rest_framework import serializers


class STKPushSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    reference = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=255)
