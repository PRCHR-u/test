import logging
import time
import shutil
from django.db import connections, DatabaseError
from django.http import JsonResponse
from django.views import View
from django.conf import settings
from django.core.cache import cache
from django.db.migrations.executor import MigrationExecutor

logger = logging.getLogger('health')


class HealthCheckView(View):
    """
    Комплексная проверка здоровья приложения
    """

    def get(self, request):
        checks = {}
        overall_status = 'healthy'

        # Проверка базы данных
        checks['database'] = self._check_database()

        # Проверка кэша (если используется Redis/Memcached)
        checks['cache'] = self._check_cache()

        # Проверка дискового пространства
        checks['storage'] = self._check_storage()

        # Определяем общий статус
        for check_name, check_result in checks.items():
            if not check_result.get('healthy', False):
                overall_status = 'unhealthy'
                logger.error(f"Health check failed: {check_name} - {check_result}")

        response_data = {
            'status': overall_status,
            'timestamp': time.time(),
            'checks': checks
        }

        status_code = 200 if overall_status == 'healthy' else 503
        return JsonResponse(response_data, status=status_code)

    def _check_database(self):
        """Проверка подключения к базе данных"""
        try:
            start_time = time.time()
            connections['default'].cursor().execute("SELECT 1")
            db_time = time.time() - start_time

            return {
                'healthy': True,
                'response_time': round(db_time * 1000, 2),  # мс
                'details': 'Database connection successful'
            }
        except DatabaseError as e:
            return {
                'healthy': False,
                'error': str(e),
                'details': 'Database connection failed'
            }

    def _check_cache(self):
        """Проверка кэша"""
        try:
            start_time = time.time()

            # Тест записи
            test_key = 'health_check_test'
            test_value = 'test_value'
            cache.set(test_key, test_value, 5)

            # Тест чтения
            retrieved_value = cache.get(test_key)

            cache_time = time.time() - start_time

            if retrieved_value == test_value:
                return {
                    'healthy': True,
                    'response_time': round(cache_time * 1000, 2),
                    'details': 'Cache is working correctly'
                }
            else:
                return {
                    'healthy': False,
                    'error': 'Cache read/write test failed',
                    'details': 'Cache data corruption'
                }

        except Exception as e:
            return {
                'healthy': False,
                'error': str(e),
                'details': 'Cache connection failed'
            }

    def _check_storage(self):
        """Проверка дискового пространства"""
        try:
            # Проверяем доступное место на диске
            stat = shutil.disk_usage(settings.BASE_DIR)
            total_gb = stat.total / (1024**3)
            free_gb = stat.free / (1024**3)
            free_percent = (stat.free / stat.total) * 100

            # Считаем здоровым если свободно больше 10%
            is_healthy = free_percent > 10.0

            return {
                'healthy': is_healthy,
                'total_gb': round(total_gb, 2),
                'free_gb': round(free_gb, 2),
                'free_percent': round(free_percent, 2),
                'details': f'Storage: {free_percent:.1f}% free'
            }
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e),
                'details': 'Storage check failed'
            }


class SimpleHealthCheckView(View):
    """
    Упрощенная проверка здоровья для Load Balancer
    """
    def get(self, request):
        try:
            # Базовая проверка БД
            connections['default'].cursor().execute("SELECT 1")

            return JsonResponse({
                'status': 'healthy',
                'timestamp': time.time()
            })
        except Exception as e:
            logger.error(f"Simple health check failed: {str(e)}")
            return JsonResponse({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': time.time()
            }, status=503)


class ReadinessCheckView(View):
    """
    Проверка готовности приложения (Readiness Probe)
    """
    def get(self, request):
        checks = {}

        # Проверка базы данных
        try:
            connections['default'].cursor().execute("SELECT 1")
            checks['database'] = True
        except Exception as e:
            checks['database'] = False
            logger.error(f"Readiness check - Database failed: {str(e)}")

        # Проверка миграций
        try:
            executor = MigrationExecutor(connections['default'])
            plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
            checks['migrations'] = len(plan) == 0  # Все миграции применены
        except Exception as e:
            checks['migrations'] = False
            logger.error(f"Readiness check - Migrations failed: {str(e)}")

        all_ready = all(checks.values())

        response_data = {
            'ready': all_ready,
            'checks': checks,
            'timestamp': time.time()
        }

        status_code = 200 if all_ready else 503
        return JsonResponse(response_data, status=status_code)


class LivenessCheckView(View):
    """
    Проверка живости приложения (Liveness Probe)
    """
    def get(self, request):
        # Простая проверка - приложение отвечает на запросы
        return JsonResponse({
            'alive': True,
            'timestamp': time.time()
        })
