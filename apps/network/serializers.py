from rest_framework import serializers
from .models import NetworkNode, Product


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for the Product model.
    """

    class Meta:
        model = Product
        exclude = ('id',)


class NetworkNodeSerializer(serializers.ModelSerializer):
    """
    Serializer for the NetworkNode model.

    The 'debt' field is read-only as required.
    Products associated with the node are included for comprehensive data representation.
    """
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = NetworkNode
        fields = (
            'id', 'name', 'node_type', 'email', 'country', 'city',
            'street', 'house_number', 'products', 'supplier', 'debt', 'created_at'
        )
        read_only_fields = ('debt', 'created_at')
        depth = 1  # Include one level of nested relationship data (for supplier).
