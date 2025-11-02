
import logging
from rest_framework import serializers
from django.db import transaction
from apps.network.models import NetworkNode, SupplierLink, Product

# Получаем логгер с именем 'business'
business_logger = logging.getLogger('business')


class ProductSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Product с логированием."""
    class Meta:
        model = Product
        fields = '__all__'

    def create(self, validated_data):
        product = super().create(validated_data)
        business_logger.info(f"Через API создан новый продукт: '{product.name}' (ID: {product.id}).")
        return product

    def update(self, instance, validated_data):
        product = super().update(instance, validated_data)
        business_logger.info(f"Черезе API обновлен продукт: '{product.name}' (ID: {product.id}).")
        return product


class SupplierLinkSerializer(serializers.ModelSerializer):
    """Сериализатор для модели SupplierLink. Поле debt - только для чтения."""
    class Meta:
        model = SupplierLink
        fields = ('id', 'supplier', 'client', 'debt')
        read_only_fields = ('debt',)


class NetworkNodeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели NetworkNode с логированием и обработкой бизнес-логики."""
    suppliers_links = SupplierLinkSerializer(source='client_links', many=True, read_only=True)
    products = ProductSerializer(many=True, read_only=True)
    level = serializers.SerializerMethodField()
    
    # Поле только для записи. Позволяет указать ID поставщика при создании/обновлении.
    supplier_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = NetworkNode
        fields = (
            'id', 'name', 'node_type', 'level', 'email', 'country', 'city',
            'street', 'house_number', 'products', 'suppliers_links', 'created_at',
            'supplier_id'  # Добавляем поле для возможности записи
        )

    def get_level(self, obj):
        return obj.get_level()

    def validate_supplier_id(self, value):
        """Проверяет, существует ли узел поставщика с указанным ID."""
        if value is not None and not NetworkNode.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Узел поставщика с указанным ID не существует.")
        return value

    def validate(self, data):
        """Проверяет бизнес-логику: запрет на цикличные зависимости."""
        if 'supplier_id' not in data:
            return data

        supplier_id = data.get('supplier_id')
        instance = self.instance  # Узел, который мы обновляем

        if instance and supplier_id:
            # Проверяем, не пытаемся ли мы сделать дочерний узел своим же поставщиком
            current = NetworkNode.objects.get(pk=supplier_id)
            while current:
                if current == instance:
                    # Логируем попытку нарушения бизнес-правила
                    business_logger.warning(
                        f"Попытка создать циклическую зависимость: "
                        f"сделать узел '{instance.name}' (ID: {instance.id}) зависимым от своего дочернего узла "
                        f"(ID: {supplier_id}). Операция отклонена."
                    )
                    raise serializers.ValidationError({'supplier_id': "Невозможно установить циклическую зависимость."}) 
                
                # Поднимаемся вверх по иерархии
                # В нашей модели может быть несколько поставщиков, берем первого
                link = current.client_links.first()
                current = link.supplier if link else None
        
        return data

    @transaction.atomic
    def create(self, validated_data):
        supplier_id = validated_data.pop('supplier_id', None)
        node = NetworkNode.objects.create(**validated_data)

        if supplier_id:
            SupplierLink.objects.create(supplier_id=supplier_id, client=node)

        business_logger.info(f"Через API создан новый узел сети: '{node.name}' (ID: {node.id}).")
        return node

    @transaction.atomic
    def update(self, instance, validated_data):
        supplier_id = validated_data.pop('supplier_id', None)

        # Обновляем поля самого узла
        instance = super().update(instance, validated_data)

        # Обновляем связь с поставщиком
        if supplier_id is not None:
            # Удаляем старую связь
            instance.client_links.all().delete()
            # Создаем новую связь
            SupplierLink.objects.create(supplier_id=supplier_id, client=instance)
        
        business_logger.info(f"Через API обновлен узел сети: '{instance.name}' (ID: {instance.id}).")
        return instance
