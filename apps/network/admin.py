
import logging
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html

from .models import NetworkNode, Product, SupplierLink

# Получаем логгер с именем 'business' из настроек settings.py
business_logger = logging.getLogger('business')


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
    readonly_fields = ('debt',)
    actions = ['clear_debt']

    @admin.action(description='Очистить задолженность у выбранных связей')
    def clear_debt(self, request: HttpRequest, queryset: QuerySet[SupplierLink]):
        """Действие для обнуления задолженности с логированием."""

        # --- Логирование действия ---
        admin_user = request.user.username
        # Итерируемся по queryset ПЕРЕД обновлением, чтобы залогировать старые значения
        for link in queryset:
            business_logger.info(
                f"Администратор '{admin_user}' очистил задолженность для узла '{link.client.name}' "
                f"(поставщик: {link.supplier.name}). Старая задолженность: {link.debt}."
            )
        # --- Конец логирования ---

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
        links = obj.client_links.select_related('supplier').all()
        if not links:
            return "—"

        supplier_html = []
        for link in links:
            supplier_url = reverse("admin:network_networknode_change", args=[link.supplier.id])
            supplier_html.append(
                f'<a href="{supplier_url}">{link.supplier.name}</a> (Долг: {link.debt} ₽)'
            )
        return format_html("<br>".join(supplier_html))

    display_suppliers_and_debt.short_description = 'Поставщик и задолженность'

    def get_queryset(self, request: HttpRequest) -> QuerySet[NetworkNode]:
        """
        Оптимизирует запросы к БД, чтобы избежать проблемы N+1.
        """
        return super().get_queryset(request).prefetch_related('client_links__supplier')
