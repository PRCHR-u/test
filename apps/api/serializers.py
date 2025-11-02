from rest_framework import serializers
from apps.network.models import NetworkNode, SupplierLink, Product


class ProductSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Product."""
    class Meta:
        model = Product
        fields = '__all__'


class SupplierLinkSerializer(serializers.ModelSerializer):
    """Сериализатор для модели SupplierLink. Поле debt - только для чтения."""
    class Meta:
        model = SupplierLink
        fields = ('id', 'supplier', 'client', 'debt')
        read_only_fields = ('debt', )  # Запрещаем обновление поля debt через API


class NetworkNodeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели NetworkNode."""
    # Включаем вложенный просмотр поставщиков с их задолженностями
    suppliers_links = SupplierLinkSerializer(source='client_links', many=True, read_only=True)
    products = ProductSerializer(many=True, read_only=True)
    level = serializers.SerializerMethodField()

    class Meta:
        model = NetworkNode
        fields = (
            'id', 'name', 'node_type', 'level', 'email', 'country', 'city', 
            'street', 'house_number', 'products', 'suppliers_links', 'created_at'
        )
    
    def get_level(self, obj):
        """Вызывает метод get_level модели NetworkNode."""
        return obj.get_level()

