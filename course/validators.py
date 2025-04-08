from urllib.parse import urlparse
from django.core.exceptions import ValidationError


def validate_youtube_link(value):
    if not value.startswith(("http://", "https://")):
        raise ValidationError("Ссылка должна начинаться с http:// или https://")

    parsed_url = urlparse(value)

    if "youtube.com" not in parsed_url.hostname:
        raise ValidationError("Можно прикреплять только ссылки на youtube.com")

    return value
