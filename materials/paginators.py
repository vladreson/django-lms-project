from rest_framework.pagination import PageNumberPagination


class MaterialsPaginator(PageNumberPagination):
    """
    Пагинатор для курсов и уроков
    """
    page_size = 10  # Количество элементов на странице по умолчанию
    page_size_query_param = 'page_size'  # Параметр для изменения количества элементов на странице
    max_page_size = 50  # Максимальное количество элементов на странице


class SubscriptionPaginator(PageNumberPagination):
    """
    Пагинатор для подписок
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100