from rest_framework import viewsets, permissions
from apps.network.models import NetworkNode, Product
from .serializers import NetworkNodeSerializer, ProductSerializer


class IsActiveUser(permissions.BasePermission):
    """
    Кастомное разрешение, которое проверяет, что пользователь является активным сотрудником.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_active


class NetworkNodeViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели NetworkNode.
    Предоставляет CRUD операции через API.
    Доступно только для активных сотрудников.
    """
    queryset = NetworkNode.objects.all()
    serializer_class = NetworkNodeSerializer
    permission_classes = [IsActiveUser]
    filterset_fields = ['country'] # Добавляем возможность фильтрации по стране


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели Product.
    Предоставляет CRUD операции через API.
    Доступно только для активных сотрудников.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsActiveUser]

