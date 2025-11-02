
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.network.models import NetworkNode, Product
from decimal import Decimal

# Получаем модель пользователя, которая используется в проекте
User = get_user_model()


class APITests(APITestCase):
    """
    Набор тестов для проверки API эндпоинтов.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Метод для создания начальных данных, которые будут использоваться во всех тестах этого класса.
        """
        # 1. Создаем тестового пользователя
        cls.test_user = User.objects.create_user(
            username='testuser',
            password='testpassword123',
            email='test@example.com',
            is_active=True
        )

        # 2. Создаем объекты NetworkNode
        cls.node1 = NetworkNode.objects.create(name="Завод", country="Россия", city="Москва", debt=100.00)
        cls.node2 = NetworkNode.objects.create(name="Дистрибьютор", country="Россия", city="СПБ", supplier=cls.node1)
        cls.node3 = NetworkNode.objects.create(name="Магазин", country="Беларусь", city="Минск", supplier=cls.node2)

        # 3. Создаем объекты Product
        cls.product1 = Product.objects.create(name="Лэптоп", model="Модель X", release_date="2023-01-01")

        # 4. Определяем URL'ы
        cls.nodes_url = reverse('networknode-list')
        cls.products_url = reverse('product-list')

    def setUp(self):
        """Аутентифицируем клиента перед каждым тестом."""
        self.client.force_authenticate(user=self.test_user)

    # --- Тесты для NetworkNode (Модульные) ---
    def test_create_node_with_invalid_data_fails(self):
        """Тест: Попытка создания узла с невалидными данными."""
        response = self.client.post(self.nodes_url, {'country': 'KЗ', 'city': 'Алматы'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_node_debt_is_ignored(self):
        """Тест: Попытка обновления поля debt через API игнорируется."""
        url = reverse('networknode-detail', args=[self.node1.id])
        initial_debt = self.node1.debt
        response = self.client.patch(url, {'debt': '9999.99'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.node1.refresh_from_db()
        self.assertEqual(self.node1.debt, initial_debt)

    # --- Тесты для NetworkNode (Интеграционные) ---
    def test_cannot_set_self_as_supplier(self):
        """Интеграционный тест: Нельзя установить узел поставщиком самому себе."""
        url = reverse('networknode-detail', args=[self.node1.id])
        data = {'supplier': self.node1.id}
        response = self.client.patch(url, data, format='json')
        
        # Ожидаем ошибку валидации
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('supplier', response.data) # Проверяем, что ошибка именно в поле supplier

    def test_cannot_create_circular_dependency(self):
        """Интеграционный тест: Нельзя создать циклическую зависимость в иерархии."""
        # У нас есть цепочка: node1 (Завод) -> node2 (Дистрибьютор) -> node3 (Магазин)
        # Пытаемся сделать поставщиком для Завода (node1) Магазин (node3)
        # Это должно создать цикл: node1 -> node2 -> node3 -> node1
        url = reverse('networknode-detail', args=[self.node1.id])
        data = {'supplier': self.node3.id}
        response = self.client.patch(url, data, format='json')
        
        # Ожидаем ошибку валидации
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('supplier', response.data)
