
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.network.models import NetworkNode, Product
from decimal import Decimal

# Получаем модель пользователя, которая используется в проекте
User = get_user_model()


class NetworkNodeAPITests(APITestCase):
    """
    Набор тестов для эндпоинтов модели NetworkNode.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Метод для создания начальных данных, которые будут использоваться во всех тестах этого класса.
        """
        # 1. Создаем тестовых пользователей
        cls.active_user = User.objects.create_user(
            username='active_user', password='password123', is_active=True
        )
        cls.inactive_user = User.objects.create_user(
            username='inactive_user', password='password123', is_active=False
        )

        # 2. Создаем объекты NetworkNode
        cls.node1 = NetworkNode.objects.create(name="Завод", country="Россия", city="Москва", debt=Decimal("100.50"))
        cls.node2 = NetworkNode.objects.create(name="Дистрибьютор", country="Россия", city="СПБ", supplier=cls.node1)
        cls.node3 = NetworkNode.objects.create(name="Магазин", country="Беларусь", city="Минск", supplier=cls.node2)

        # 3. Определяем URL'ы
        cls.nodes_list_url = reverse('networknode-list')
        cls.node_detail_url = reverse('networknode-detail', args=[cls.node2.id])

    def setUp(self):
        """Аутентифицируем клиента перед каждым тестом."""
        self.client.force_authenticate(user=self.active_user)

    # --- Тесты прав доступа ---

    def test_unauthenticated_user_cannot_access(self):
        """Тест: Неаутентифицированный пользователь не имеет доступа к API."""
        self.client.logout()
        response = self.client.get(self.nodes_list_url)
        # В зависимости от настроек (AllowAny vs IsAuthenticated) будет 401 или 403
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_inactive_user_cannot_access(self):
        """Тест: Неактивный пользователь не имеет доступа к API."""
        self.client.force_authenticate(user=self.inactive_user)
        response = self.client.get(self.nodes_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- Тесты CRUD для NetworkNode ---

    def test_list_nodes(self):
        """Тест: Получение списка узлов."""
        response = self.client.get(self.nodes_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)

    def test_retrieve_node(self):
        """Тест: Получение одного узла."""
        response = self.client.get(self.node_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.node2.name)

    def test_create_node(self):
        """Тест: Успешное создание узла."""
        data = {'name': 'Новый Ритейлер', 'country': 'Казахстан', 'city': 'Астана', 'supplier': self.node1.id}
        response = self.client.post(self.nodes_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(NetworkNode.objects.filter(name='Новый Ритейлер').exists())

    def test_update_node(self):
        """Тест: Успешное обновление узла."""
        data = {'name': 'Обновленный Дистрибьютор'}
        response = self.client.patch(self.node_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.node2.refresh_from_db()
        self.assertEqual(self.node2.name, 'Обновленный Дистрибьютор')

    def test_delete_node(self):
        """Тест: Успешное удаление узла."""
        url = reverse('networknode-detail', args=[self.node3.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(NetworkNode.objects.filter(id=self.node3.id).exists())

    # --- Тесты фильтрации и бизнес-логики ---
    
    def test_filter_by_country(self):
        """Тест: Фильтрация списка узлов по стране."""
        response = self.client.get(self.nodes_list_url, {'country': 'Беларусь'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], self.node3.name)

    def test_update_node_debt_is_ignored(self):
        """Тест: Попытка обновления поля debt через API игнорируется."""
        initial_debt = self.node1.debt
        response = self.client.patch(reverse('networknode-detail', args=[self.node1.id]), {'debt': '9999.99'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.node1.refresh_from_db()
        self.assertEqual(self.node1.debt, initial_debt)

    def test_cannot_set_self_as_supplier(self):
        """Интеграционный тест: Нельзя установить узел поставщиком самому себе."""
        response = self.client.patch(self.node_detail_url, {'supplier': self.node2.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_create_circular_dependency(self):
        """Интеграционный тест: Нельзя создать циклическую зависимость."""
        # node1 -> node2 -> node3. Пытаемся сделать node1.supplier = node3
        url = reverse('networknode-detail', args=[self.node1.id])
        response = self.client.patch(url, {'supplier': self.node3.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('supplier', response.data)


class ProductAPITests(APITestCase):
    """
    Набор тестов для эндпоинтов модели Product.
    """
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='product_user', password='password123', is_active=True)
        cls.product = Product.objects.create(name="Лэптоп", model="Модель X", release_date="2023-01-01")
        cls.products_list_url = reverse('product-list')
        cls.product_detail_url = reverse('product-detail', args=[cls.product.id])

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_list_products(self):
        """Тест: Получение списка продуктов."""
        response = self.client.get(self.products_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_product(self):
        """Тест: Создание продукта."""
        data = {"name": "Смартфон", "model": "Модель Y", "release_date": "2024-02-02"}
        response = self.client.post(self.products_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_product(self):
        """Тест: Получение одного продукта."""
        response = self.client.get(self.product_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.product.name)

    def test_update_product(self):
        """Тест: Обновление продукта."""
        data = {"model": "Модель X Pro"}
        response = self.client.patch(self.product_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.model, "Модель X Pro")

    def test_delete_product(self):
        """Тест: Удаление продукта."""
        response = self.client.delete(self.product_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())
