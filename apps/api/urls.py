from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .views import NetworkNodeViewSet, ProductViewSet

# Создаем роутер для автоматического определения URL-адресов
router = DefaultRouter()
router.register(r'nodes', NetworkNodeViewSet, basename='networknode')
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
    # Эндпоинт для получения токена аутентификации
    path('token/', obtain_auth_token, name='api_token_auth'),
]
