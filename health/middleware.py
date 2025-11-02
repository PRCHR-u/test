import time
import logging
from django.conf import settings
from django.db import connection

logger = logging.getLogger('metrics')


class MetricsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Игнорируем запросы к мониторингу
        if request.path.startswith('/monitoring/'):
            return self.get_response(request)

        start_time = time.time()
        db_queries_before = len(connection.queries) if settings.DEBUG else 0

        response = self.get_response(request)

        processing_time = time.time() - start_time
        db_queries_after = len(connection.queries) if settings.DEBUG else 0
        db_queries_count = db_queries_after - db_queries_before

        # Логируем метрики
        logger.info(
            f"REQUEST_METRICS: method={request.method} "
            f"path={request.path} "
            f"status={response.status_code} "
            f"time={processing_time:.3f}s "
            f"queries={db_queries_count}"
        )

        return response
