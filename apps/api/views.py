import logging
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from apps.network.models import NetworkNode, Product
from .serializers import NetworkNodeSerializer, ProductSerializer
from .pagination import CustomPagination

# Получаем логгер 'apps', который мы настроили для общих событий приложения
app_logger = logging.getLogger('apps')


class IsActiveUser(permissions.BasePermission):
    """
    Кастомное разрешение, которое проверяет, что пользователь является активным сотрудником.
    """
    def has_permission(self, request, view):
        # Логируем попытку доступа
        if not (request.user and request.user.is_authenticated and request.user.is_active):
            app_logger.warning(
                f"Неавторизованный доступ к {view.basename} отклонен. "
                f"User: {request.user}, IP: {request.META.get('REMOTE_ADDR')}"
            )
            return False
        return True


class NetworkNodeViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели NetworkNode с расширенным логированием.
    """
    queryset = NetworkNode.objects.all().prefetch_related('products', 'client_links__supplier')
    serializer_class = NetworkNodeSerializer
    permission_classes = [IsActiveUser]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['country', 'city']
    search_fields = ['name']

    def list(self, request, *args, **kwargs):
        """Переопределяем метод для логирования параметров запроса."""
        country_filter = request.query_params.get('country')
        city_filter = request.query_params.get('city')
        search_query = request.query_params.get('search')

        log_message = f"Пользователь '{request.user.username}' запросил список узлов сети."
        if country_filter or city_filter or search_query:
            log_message += " Параметры запроса:"
            if country_filter:
                log_message += f" страна='{country_filter}'"
            if city_filter:
                log_message += f" город='{city_filter}'"
            if search_query:
                log_message += f" поиск='{search_query}'"

        app_logger.info(log_message)

        return super().list(request, *args, **kwargs)


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели Product.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsActiveUser]
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
