
from django.contrib import admin
from .models import NetworkNode, Product, SupplierLink

@admin.register(NetworkNode)
class NetworkNodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'node_type', 'city', 'created_at')
    list_filter = ('node_type', 'city')
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'model', 'release_date')

@admin.register(SupplierLink)
class SupplierLinkAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'client', 'debt')
