from rest_framework.exceptions import ValidationError


class YoutubeLinkValidator:
    """
    Проверка, что ссылка в поле ведет на ресурс youtube.com
    """

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        template = "https://www.youtube.com"

        str_value = value.get(self.field)

        if str_value:
            if not str_value.startswith(template):
                raise ValidationError(
                    "Ссылка может быть только видео сервис youtube.com"
                )
