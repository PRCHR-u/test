
from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker
import random

from apps.network.models import NetworkNode, Product, SupplierLink

class Command(BaseCommand):
    """
    Django-команда для заполнения базы данных тестовыми данными.

    Генерирует иерархическую структуру поставщиков с использованием единой модели NetworkNode:
    - 3 Завода (уровень 0)
    - 5 Розничных сетей (уровень 1), случайным образом связанных с заводами.
    - 10 Индивидуальных предпринимателей (уровень 2), случайным образом связанных 
      с розничными сетями.

    Каждый узел сети получает случайные контакты и набор продуктов.
    Задолженность генерируется в связях между узлами.
    """
    help = 'Заполняет базу данных тестовыми иерархическими данными для модели NetworkNode.'

    def handle(self, *args, **kwargs):
        # Используем транзакцию, чтобы гарантировать целостность данных.
        with transaction.atomic():
            self.stdout.write("Удаление старых данных...")
            # Очищаем все модели
            SupplierLink.objects.all().delete()
            NetworkNode.objects.all().delete()
            Product.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Старые данные успешно удалены."))

            fake = Faker('ru_RU')

            # --- Создание Продуктов ---
            self.stdout.write("Создание продуктов...")
            products = []
            for _ in range(20): # Создадим 20 уникальных продуктов
                product = Product.objects.create(
                    name=fake.word().capitalize() + " " + fake.word(),
                    model=fake.bothify(text='??-####'),
                    release_date=fake.date_between(start_date='-5y', end_date='today')
                )
                products.append(product)
            self.stdout.write(self.style.SUCCESS(f"Создано {len(products)} продуктов."))

            # --- Создание Заводов (Уровень 0) ---
            self.stdout.write("Создание заводов...")
            factories = []
            for _ in range(3):
                factory = NetworkNode.objects.create(
                    name=f"Завод «{fake.company()}»",
                    node_type=NetworkNode.NodeType.FACTORY,
                    email=fake.unique.email(),
                    country=fake.country(),
                    city=fake.city(),
                    street=fake.street_name(),
                    house_number=fake.building_number(),
                )
                # Добавляем заводу случайные продукты
                factory.products.set(random.sample(products, k=random.randint(5, 15)))
                factories.append(factory)
            self.stdout.write(self.style.SUCCESS(f"Создано {len(factories)} заводов."))

            # --- Создание Розничных сетей (Уровень 1) ---
            self.stdout.write("Создание розничных сетей...")
            retail_networks = []
            if factories:
                for _ in range(5):
                    supplier_factory = random.choice(factories)
                    network = NetworkNode.objects.create(
                        name=f"Сеть «{fake.company()}»",
                        node_type=NetworkNode.NodeType.RETAIL,
                        email=fake.unique.email(),
                        country=fake.country(),
                        city=fake.city(),
                        street=fake.street_name(),
                        house_number=fake.building_number(),
                    )
                    # Создаем связь с поставщиком (заводом) и указываем долг
                    SupplierLink.objects.create(
                        supplier=supplier_factory,
                        client=network,
                        debt=fake.pydecimal(left_digits=5, right_digits=2, positive=True, min_value=1000, max_value=50000)
                    )
                    # Копируем некоторые продукты от поставщика
                    supplier_products = list(supplier_factory.products.all())
                    if supplier_products:
                        network.products.set(random.sample(supplier_products, k=min(len(supplier_products), random.randint(3, 10))))
                    
                    retail_networks.append(network)
            self.stdout.write(self.style.SUCCESS(f"Создано {len(retail_networks)} розничных сетей."))

            # --- Создание Индивидуальных предпринимателей (Уровень 2) ---
            self.stdout.write("Создание индивидуальных предпринимателей...")
            entrepreneurs = []
            if retail_networks:
                for _ in range(10):
                    supplier_network = random.choice(retail_networks)
                    ip = NetworkNode.objects.create(
                        name=f"ИП {fake.last_name()} {fake.first_name()}",
                        node_type=NetworkNode.NodeType.ENTREPRENEUR,
                        email=fake.unique.email(),
                        country=fake.country(),
                        city=fake.city(),
                        street=fake.street_name(),
                        house_number=fake.building_number(),
                    )
                    # Создаем связь с поставщиком (розничной сетью) и указываем долг
                    SupplierLink.objects.create(
                        supplier=supplier_network,
                        client=ip,
                        debt=fake.pydecimal(left_digits=4, right_digits=2, positive=True, min_value=500, max_value=10000)
                    )
                    # Копируем продукты от поставщика
                    supplier_products = list(supplier_network.products.all())
                    if supplier_products:
                        ip.products.set(random.sample(supplier_products, k=min(len(supplier_products), random.randint(2, 5))))

                    entrepreneurs.append(ip)
            self.stdout.write(self.style.SUCCESS(f"Создано {len(entrepreneurs)} индивидуальных предпринимателей."))

        self.stdout.write(self.style.SUCCESS("\nБаза данных успешно заполнена тестовыми данными!"))

