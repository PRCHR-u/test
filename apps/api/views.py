from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from apps.network.models import NetworkNode, Product
from .serializers import NetworkNodeSerializer, ProductSerializer
from .pagination import CustomPagination  # Импортируем наш класс пагинации


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
    pagination_class = CustomPagination
    
    # бэкенды фильтрации
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['country', 'city']
    search_fields = ['name']


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели Product.
    Предоставляет CRUD операции через API.
    Доступно только для активных сотрудников.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsActiveUser]
    pagination_class = CustomPagination  # Подключаем пагинацию

    # Добавляем поиск по названию
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
