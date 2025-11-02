import psutil
from django.http import JsonResponse
from django.views import View
import logging
from django.apps import apps
from django.contrib.auth import get_user_model
from apps.network.models import NetworkNode, Product  # Уточненный импорт

logger = logging.getLogger('metrics')
User = get_user_model()


class MetricsView(View):
    """
    Prometheus-подобные метрики для мониторинга
    """

    def get(self, request):
        metrics = {}

        # Системные метрики
        metrics.update(self._get_system_metrics())

        # Метрики приложения
        metrics.update(self._get_application_metrics())

        # Метрики базы данных (может быть медленным, будьте осторожны)
        # metrics.update(self._get_database_metrics())

        return JsonResponse(metrics)

    def _get_system_metrics(self):
        """
        Системные метрики
        """
        try:
            # Использование CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)

            # Использование памяти
            memory = psutil.virtual_memory()

            # Дисковое пространство
            disk = psutil.disk_usage('/')

            return {
                'system_cpu_percent': cpu_percent,
                'system_memory_total': memory.total,
                'system_memory_available': memory.available,
                'system_memory_used_percent': memory.percent,
                'system_disk_total': disk.total,
                'system_disk_used': disk.used,
                'system_disk_free': disk.free,
                'system_disk_used_percent': (disk.used / disk.total) * 100,
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {str(e)}")
            return {}

    def _get_application_metrics(self):
        """
        Метрики приложения
        """
        try:
            # Количество пользователей
            total_users = User.objects.count()
            active_users = User.objects.filter(is_active=True).count()

            # Количество моделей в приложениях
            model_counts = {}
            for app_config in apps.get_app_configs():
                if app_config.name.startswith('apps.'):
                    model_count = len(app_config.get_models())
                    model_counts[app_config.label] = model_count

            return {
                'application_users_total': total_users,
                'application_users_active': active_users,
                'application_models_by_app': model_counts,
            }
        except Exception as e:
            logger.error(f"Error getting application metrics: {str(e)}")
            return {}


class BusinessMetricsView(View):
    """
    Бизнес-метрики приложения
    """

    def get(self, request):
        try:
            metrics = {
                'business': {
                    'users': {
                        'total': User.objects.count(),
                        'active': User.objects.filter(is_active=True).count(),
                    },
                    'network_nodes': {
                        'total': NetworkNode.objects.count(),
                        'factories': NetworkNode.objects.filter(type='factory').count(),
                        'retailers': NetworkNode.objects.filter(type='retail').count(),
                        'entrepreneurs': NetworkNode.objects.filter(type='individual_entrepreneur').count(),
                    },
                    'products': {
                        'total': Product.objects.count(),
                    }
                }
            }

            return JsonResponse(metrics)
        except Exception as e:
            logger.error(f"Error getting business metrics: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
