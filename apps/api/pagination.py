from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """
    Кастомный класс пагинации для установки стандартного размера страницы
    и возможности его изменения клиентом.
    """
    page_size = 10  # Количество объектов на странице по умолчанию
    page_size_query_param = 'page_size'  # Параметр для изменения размера страницы (e.g., /api/nodes/?page_size=100)
    max_page_size = 1000  # Максимально допустимый размер страницы
