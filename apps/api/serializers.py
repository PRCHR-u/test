
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
        # Запрещаем обновление поля debt через API.
        # Причина: задолженность должна обновляться на основе действий (например, оплата),
        # а не прямого редактирования, чтобы обеспечить целостность данных.
        read_only_fields = ('debt',)


class NetworkNodeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели NetworkNode."""
    # Включаем вложенный просмотр поставщиков с их задолженностями.
    # `source='client_links'` указывает, что для этого поля нужно использовать 
    # related_name `client_links` из модели NetworkNode.
    suppliers_links = SupplierLinkSerializer(source='client_links', many=True, read_only=True)
    
    # Отображаем полный список продуктов, связанных с узлом.
    products = ProductSerializer(many=True, read_only=True)
    
    # Динамическое поле, которое вычисляет иерархический уровень узла.
    level = serializers.SerializerMethodField()

    class Meta:
        model = NetworkNode
        fields = (
            'id', 'name', 'node_type', 'level', 'email', 'country', 'city', 
            'street', 'house_number', 'products', 'suppliers_links', 'created_at'
        )
    
    def get_level(self, obj):
        """Вызывает метод get_level модели NetworkNode для вычисления уровня."""
        # Этот метод позволяет нам добавить в API поле `level`, 
        # которого нет в базе данных, но есть бизнес-логика для его расчета.
        return obj.get_level()
