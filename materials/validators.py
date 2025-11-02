from django.core.exceptions import ValidationError
from urllib.parse import urlparse
import re


def validate_youtube_url(value):
    """
    Валидатор для проверки что ссылка ведет на YouTube
    """
    if not value:
        return

    # Парсим URL
    parsed_url = urlparse(value)

    # Проверяем домен
    allowed_domains = ['youtube.com', 'www.youtube.com', 'youtu.be']
    domain = parsed_url.netloc.lower()

    # Проверяем что домен в списке разрешенных
    is_valid_domain = any(allowed_domain in domain for allowed_domain in allowed_domains)

    if not is_valid_domain:
        raise ValidationError(
            'Разрешены только ссылки на YouTube. '
            'Пример: https://www.youtube.com/watch?v=VIDEO_ID'
        )

    # Дополнительная проверка для youtu.be
    if 'youtu.be' in domain:
        # Для коротких ссылок проверяем что есть ID видео
        path = parsed_url.path.strip('/')
        if not path:
            raise ValidationError('Некорректная ссылка YouTube')


class YouTubeValidator:
    """
    Класс-валидатор для проверки YouTube ссылок
    """

    def __call__(self, value):
        validate_youtube_url(value)