from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend

from .models import NetworkNode
from .serializers import NetworkNodeSerializer
from .permissions import IsActiveEmployee


class NetworkNodeViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for performing CRUD operations on NetworkNode instances.

    Provides filtering by country and ensures that only active employees can access it.
    """
    queryset = NetworkNode.objects.all().select_related('supplier').prefetch_related('products')
    serializer_class = NetworkNodeSerializer
    permission_classes = [IsAdminUser, IsActiveEmployee]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['country']
