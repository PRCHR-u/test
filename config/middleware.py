import logging
import time

# Логгер 'apps' теперь будет использоваться для логирования всех запросов
logger = logging.getLogger('apps')


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Фиксируем время начала обработки запроса
        start_time = time.time()

        # Логируем основную информацию о входящем запросе
        logger.info(
            f"Входящий запрос: {request.method} {request.path} "
            f"от {request.META.get('REMOTE_ADDR')} "
            f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')}"
        )

        response = self.get_response(request)

        # Вычисляем длительность обработки и логируем информацию об ответе
        duration = time.time() - start_time
        logger.info(
            f"Ответ: {request.method} {request.path} -> {response.status_code} "
            f"(время: {duration:.2f}с)"
        )

        return response
