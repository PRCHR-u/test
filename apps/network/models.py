from django.core.exceptions import ValidationError
from django.db import models


class Product(models.Model):
    """Модель продукта."""
    name = models.CharField(max_length=255, verbose_name="Название")
    model = models.CharField(max_length=255, verbose_name="Модель")
    release_date = models.DateField(verbose_name="Дата выхода на рынок")

    def __str__(self):
        return f"{self.name} {self.model}"

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"


class SupplierLink(models.Model):
    """Промежуточная модель для связи Поставщик-Клиент."""
    supplier = models.ForeignKey(
        'NetworkNode',
        on_delete=models.CASCADE,
        related_name='supplier_links',
        verbose_name="Поставщик"
    )
    client = models.ForeignKey(
        'NetworkNode',
        on_delete=models.CASCADE,
        related_name='client_links',
        verbose_name="Клиент"
    )
    debt = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Задолженность"
    )

    class Meta:
        verbose_name = "Связь Поставщик-Клиент"
        verbose_name_plural = "Связи Поставщик-Клиент"
        unique_together = ('supplier', 'client')  # Гарантируем уникальность связи

    def __str__(self):
        return f"{self.supplier} -> {self.client}"

    def clean(self):
        """Проверяет наличие циклических зависимостей перед сохранением."""
        super().clean()

        if self.supplier == self.client:
            raise ValidationError("Узел не может быть поставщиком самому себе.")

        # Рекурсивная проверка на наличие циклов
        parent = self.supplier
        while parent is not None:
            if parent == self.client:
                raise ValidationError("Обнаружена циклическая зависимость в цепочке поставок.")
            # Находим поставщика для текущего 'parent' узла
            # Мы предполагаем, что у узла может быть несколько поставщиков, но для 
            # простой проверки на циклы мы можем взять первого попавшегося. 
            # Более сложная проверка потребовала бы обхода графа.
            link = SupplierLink.objects.filter(client=parent).first()
            if link:
                parent = link.supplier
            else:
                parent = None


class NetworkNode(models.Model):
    """
    Модель узла сети.
    Может быть заводом, розничной сетью или индивидуальным предпринимателем.
    """

    class NodeType(models.IntegerChoices):
        FACTORY = 0, 'Завод'
        RETAIL = 1, 'Розничная сеть'
        ENTREPRENEUR = 2, 'Индивидуальный предприниматель'

    name = models.CharField(max_length=255, verbose_name="Название")
    node_type = models.IntegerField(choices=NodeType.choices, verbose_name="Тип узла")
    email = models.EmailField(unique=True, verbose_name="Email")
    country = models.CharField(max_length=100, verbose_name="Страна")
    city = models.CharField(max_length=100, verbose_name="Город")
    street = models.CharField(max_length=100, verbose_name="Улица")
    house_number = models.CharField(max_length=20, verbose_name="Номер дома")

    products = models.ManyToManyField(
        Product,
        related_name='network_nodes',
        verbose_name="Продукты"
    )

    # Гибкая связь "многие-ко-многим" через промежуточную модель
    suppliers = models.ManyToManyField(
        'self',
        through='SupplierLink',
        symmetrical=False,
        related_name='clients',
        verbose_name="Поставщики"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")

    def __str__(self):
        return self.name

    def get_level(self):
        """
        Рекурсивно вычисляет уровень узла в иерархии.
        Узел без поставщика имеет уровень 0.
        Уровень узла = максимальный уровень его поставщиков + 1.
        """
        # self.client_links - это связи, где данный узел является клиентом (т.е. это его поставщики)
        supplier_links = self.client_links.all()

        if not supplier_links.exists():
            return 0  # Уровень 0 для узлов без поставщиков

        # Рекурсивно вычисляем максимальный уровень среди всех поставщиков
        max_supplier_level = max(link.supplier.get_level() for link in supplier_links)
        
        return max_supplier_level + 1

    class Meta:
        verbose_name = "Узел сети"
        verbose_name_plural = "Узлы сети"
