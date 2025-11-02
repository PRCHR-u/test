from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe

from .models import NetworkNode, Product, SupplierLink


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Product model.
    """
    list_display = ('name', 'model', 'release_date')
    search_fields = ('name', 'model')


class SupplierLinkInline(admin.TabularInline):
    """
    Inline for managing supplier-client links in the NetworkNode admin.
    Allows viewing and editing supplier relationships directly.
    """
    model = SupplierLink
    fk_name = 'client'  # The foreign key from SupplierLink to NetworkNode (the client)
    extra = 1
    raw_id_fields = ('supplier',)
    verbose_name = "Поставщик"
    verbose_name_plural = "Поставщики"


@admin.register(NetworkNode)
class NetworkNodeAdmin(admin.ModelAdmin):
    """
    Admin configuration for the NetworkNode model.
    """
    list_display = ('name', 'display_supplier', 'node_type', 'level', 'city', 'country', 'created_at')
    list_filter = ('city', 'country', 'node_type')
    search_fields = ('name', 'email', 'city', 'country')
    inlines = [SupplierLinkInline]
    actions = ['clear_all_debt']
    readonly_fields = ('level', 'created_at')

    def level(self, obj: NetworkNode) -> int:
        """Вычисляет и отображает уровень иерархии узла."""
        return obj.get_level()
    
    level.short_description = 'Уровень иерархии'

    def display_supplier(self, obj: NetworkNode) -> str:
        """Отображает поставщиков узла в виде ссылок."""
        suppliers = [link.supplier for link in SupplierLink.objects.filter(client=obj)]
        if not suppliers:
            return "—"
        
        return format_html_join(
            mark_safe(', '),
            '<a href="{}">{}</a>',
            ((reverse('admin:network_networknode_change', args=[s.pk]), s.name) for s in suppliers)
        )

    display_supplier.short_description = 'Поставщик'

    @admin.action(description='Очистить всю задолженность для выбранных узлов')
    def clear_all_debt(self, request: HttpRequest, queryset: QuerySet[NetworkNode]):
        """
        Admin action to clear all debts for the selected network nodes.
        This sets the debt to 0 for all supplier links related to the selected nodes.
        """
        # The .update() method returns the number of rows affected.
        updated_count = SupplierLink.objects.filter(client__in=queryset).update(debt=0)
        
        message = f"Задолженность очищена. Количество обновленных записей: {updated_count}."
        self.message_user(request, message)
