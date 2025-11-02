
from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker
import random

from apps.network.models.factory import Factory, FactoryContacts, FactoryProducts
from apps.network.models.retail_network import RetailNetwork, RetailNetworkContacts, RetailNetworkProducts
from apps.network.models.individual_entrepreneur import IndividualEntrepreneur, IndividualEntrepreneurContacts, IndividualEntrepreneurProducts

class Command(BaseCommand):
    """
    Django-команда для заполнения базы данных тестовыми данными.

    Генерирует иерархическую структуру поставщиков:
    - 2 Завода (Factory)
    - 5 Розничных сетей (RetailNetwork), случайным образом связанных с заводами.
    - 10 Индивидуальных предпринимателей (IndividualEntrepreneur), случайным образом
      связанных с розничными сетями.

    Каждый элемент сети получает случайные контакты и список продуктов.
    """
    help = 'Заполняет базу данных тестовыми иерархическими данными сети.'

    def handle(self, *args, **kwargs):
        # Используем транзакцию, чтобы гарантировать целостность данных.
        # Если в процессе возникнет ошибка, все изменения будут отменены.
        with transaction.atomic():
            self.stdout.write("Удаление старых данных...")
            # Очищаем модели в правильном порядке, чтобы избежать проблем с внешними ключами
            IndividualEntrepreneur.objects.all().delete()
            RetailNetwork.objects.all().delete()
            Factory.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Старые данные успешно удалены."))

            # Создаем экземпляр Faker для генерации данных
            fake = Faker('ru_RU')

            # --- Создание Заводов (Уровень 0) ---
            self.stdout.write("Создание заводов...")
            factories = []
            for _ in range(2):
                factory = Factory.objects.create(name=f"Завод «{fake.company()}»")
                
                FactoryContacts.objects.create(
                    factory=factory,
                    email=fake.email(),
                    country=fake.country(),
                    city=fake.city(),
                    street=fake.street_name(),
                    house_number=fake.building_number()
                )
                
                # Создаем несколько продуктов для каждого завода
                for _ in range(random.randint(3, 7)):
                    FactoryProducts.objects.create(
                        factory=factory,
                        name=fake.word().capitalize() + " " + fake.word(),
                        model=fake.bothify(text='??-####'),
                        release_date=fake.date_between(start_date='-5y', end_date='today')
                    )
                factories.append(factory)
            self.stdout.write(self.style.SUCCESS(f"Создано {len(factories)} заводов."))

            # --- Создание Розничных сетей (Уровень 1) ---
            self.stdout.write("Создание розничных сетей...")
            retail_networks = []
            if factories:
                for _ in range(5):
                    network = RetailNetwork.objects.create(
                        name=f"Сеть «{fake.company()}»",
                        supplier=random.choice(factories),
                        debt=fake.random_int(min=1000, max=50000)
                    )
                    
                    RetailNetworkContacts.objects.create(
                        retail_network=network,
                        email=fake.email(),
                        country=fake.country(),
                        city=fake.city(),
                        street=fake.street_name(),
                        house_number=fake.building_number()
                    )

                    # Копируем некоторые продукты от поставщика (завода)
                    if network.supplier:
                        supplier_products = list(network.supplier.products.all())
                        products_to_add = random.sample(supplier_products, k=min(len(supplier_products), random.randint(2, 5)))
                        for product in products_to_add:
                            RetailNetworkProducts.objects.create(
                                retail_network=network,
                                name=product.name,
                                model=product.model,
                                release_date=product.release_date
                            )
                    retail_networks.append(network)
            self.stdout.write(self.style.SUCCESS(f"Создано {len(retail_networks)} розничных сетей."))

            # --- Создание Индивидуальных предпринимателей (Уровень 2) ---
            self.stdout.write("Создание индивидуальных предпринимателей...")
            entrepreneurs = []
            if retail_networks:
                for _ in range(10):
                    ip = IndividualEntrepreneur.objects.create(
                        name=f"ИП {fake.last_name()} {fake.first_name()}",
                        supplier=random.choice(retail_networks),
                        debt=fake.random_int(min=500, max=10000)
                    )

                    IndividualEntrepreneurContacts.objects.create(
                        individual_entrepreneur=ip,
                        email=fake.email(),
                        country=fake.country(),
                        city=fake.city(),
                        street=fake.street_name(),
                        house_number=fake.building_number()
                    )

                    # Копируем продукты от поставщика (розничной сети)
                    if ip.supplier:
                        supplier_products = list(ip.supplier.products.all())
                        products_to_add = random.sample(supplier_products, k=min(len(supplier_products), random.randint(1, 4)))
                        for product in products_to_add:
                            IndividualEntrepreneurProducts.objects.create(
                                individual_entrepreneur=ip,
                                name=product.name,
                                model=product.model,
                                release_date=product.release_date
                            )
                    entrepreneurs.append(ip)
            self.stdout.write(self.style.SUCCESS(f"Создано {len(entrepreneurs)} индивидуальных предпринимателей."))

        self.stdout.write(self.style.SUCCESS("База данных успешно заполнена тестовыми данными!"))

