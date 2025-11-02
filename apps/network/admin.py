
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html

from .models import NetworkNode, Product, SupplierLink


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Админ-панель для модели Продуктов."""
    list_display = ('name', 'model', 'release_date')
    search_fields = ('name', 'model')


@admin.register(SupplierLink)
class SupplierLinkAdmin(admin.ModelAdmin):
    """
    Админ-панель для модели Связей Поставщиков.
    """
    list_display = ('supplier', 'client', 'debt')
    search_fields = ('supplier__name', 'client__name')
    # Запрещаем прямое редактирование долга в админ-панели.
    # Причина: долг должен управляться бизнес-логикой (например, через API), а не вручную.
    readonly_fields = ('debt',)
    actions = ['clear_debt']

    @admin.action(description='Очистить задолженность у выбранных связей')
    def clear_debt(self, request: HttpRequest, queryset: QuerySet[SupplierLink]):
        """Действие для обнуления задолженности."""
        updated_count = queryset.update(debt=0)
        self.message_user(
            request,
            f"Задолженность была успешно очищена для {updated_count} связей."
        )


@admin.register(NetworkNode)
class NetworkNodeAdmin(admin.ModelAdmin):
    """
    Админ-панель для Узлов Сети.
    """
    list_display = ('name', 'node_type', 'city', 'display_suppliers_and_debt', 'created_at')
    list_filter = ('node_type', 'city')
    search_fields = ('name', 'country', 'city')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    list_per_page = 25

    def display_suppliers_and_debt(self, obj: NetworkNode) -> str:
        """
        Формирует HTML для отображения поставщиков и долга в списке узлов.
        """
        # Цель: предоставить администратору быстрый доступ к информации о поставщиках
        # и задолженности прямо из списка, а также сделать навигацию по иерархии удобной.
        links = obj.client_links.select_related('supplier').all()
        if not links:
            return "—"  # Используем em-dash для наглядного отображения отсутствия поставщиков.

        supplier_html = []
        for link in links:
            # Генерируем URL для перехода на страницу админки конкретного поставщика.
            supplier_url = reverse("admin:network_networknode_change", args=[link.supplier.id])
            supplier_html.append(
                f'<a href="{supplier_url}">{link.supplier.name}</a> (Долг: {link.debt} ₽)'
            )
        # format_html необходим для безопасного рендеринга HTML в админ-панели.
        return format_html("<br>".join(supplier_html))

    display_suppliers_and_debt.short_description = 'Поставщик и задолженность'

    def get_queryset(self, request: HttpRequest) -> QuerySet[NetworkNode]:
        """
        Оптимизирует запросы к БД, чтобы избежать проблемы N+1.
        """
        # Проблема N+1: без prefetch_related, для каждого из N узлов в списке
        # будет сделан дополнительный запрос к БД для получения его поставщиков. 
        # Это приводит к N+1 запросам.
        # Решение: prefetch_related('client_links__supplier') загружает всех связанных 
        # поставщиков одним дополнительным запросом, решая проблему производительности.
        return super().get_queryset(request).prefetch_related('client_links__supplier')

