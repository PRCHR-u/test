
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import (
    Factory, FactoryContacts, FactoryProducts,
    RetailNetwork, RetailNetworkContacts, RetailNetworkProducts,
    IndividualEntrepreneur, IndividualEntrepreneurContacts, IndividualEntrepreneurProducts
)

# Используем inline-модели для удобного редактирования связанных данных
class FactoryContactsInline(admin.StackedInline):
    model = FactoryContacts
    extra = 1

class FactoryProductsInline(admin.TabularInline):
    model = FactoryProducts
    extra = 1

class RetailNetworkContactsInline(admin.StackedInline):
    model = RetailNetworkContacts
    extra = 1

class RetailNetworkProductsInline(admin.TabularInline):
    model = RetailNetworkProducts
    extra = 1

class IndividualEntrepreneurContactsInline(admin.StackedInline):
    model = IndividualEntrepreneurContacts
    extra = 1

class IndividualEntrepreneurProductsInline(admin.TabularInline):
    model = IndividualEntrepreneurProducts
    extra = 1


@admin.register(Factory)
class FactoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name', 'contacts__city')
    inlines = [FactoryContactsInline, FactoryProductsInline]


@admin.register(RetailNetwork)
class RetailNetworkAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_supplier_link', 'debt', 'created_at')
    list_display_links = ('name',)
    search_fields = ('name', 'contacts__city')
    list_filter = ('contacts__city',)
    readonly_fields = ('debt',)
    inlines = [RetailNetworkContactsInline, RetailNetworkProductsInline]
    actions = ['clear_debt']

    def get_supplier_link(self, obj):
        if obj.supplier:
            link = reverse("admin:network_factory_change", args=[obj.supplier.id])
            return format_html(f'<a href="{link}">{obj.supplier.name}</a>')
        return "N/A"
    get_supplier_link.short_description = 'Поставщик'

    @admin.action(description='Очистить задолженность у выбранных объектов')
    def clear_debt(self, request, queryset):
        queryset.update(debt=0)
        self.message_user(request, f"Задолженность была успешно очищена для {queryset.count()} объектов.")


@admin.register(IndividualEntrepreneur)
class IndividualEntrepreneurAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_supplier_link', 'debt', 'created_at')
    list_display_links = ('name',)
    search_fields = ('name', 'contacts__city')
    list_filter = ('contacts__city',)
    readonly_fields = ('debt',)
    inlines = [IndividualEntrepreneurContactsInline, IndividualEntrepreneurProductsInline]
    actions = ['clear_debt']

    def get_supplier_link(self, obj):
        if obj.supplier:
            link = reverse("admin:network_retailnetwork_change", args=[obj.supplier.id])
            return format_html(f'<a href="{link}">{obj.supplier.name}</a>')
        return "N/A"
    get_supplier_link.short_description = 'Поставщик'

    @admin.action(description='Очистить задолженность у выбранных объектов')
    def clear_debt(self, request, queryset):
        queryset.update(debt=0)
        self.message_user(request, f"Задолженность была успешно очищена для {queryset.count()} объектов.")

# Можно также зарегистрировать модели контактов и продуктов отдельно,
# но они уже доступны для редактирования внутри основных моделей.
# admin.site.register(FactoryContacts)
# admin.site.register(FactoryProducts)
# admin.site.register(RetailNetworkContacts)
# admin.site.register(RetailNetworkProducts)
# admin.site.register(IndividualEntrepreneurContacts)
# admin.site.register(IndividualEntrepreneurProducts)

