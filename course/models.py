from django.db import models


class Course(models.Model):
    title = models.CharField(
        max_length=255,
        verbose_name="Название",
        help_text="Укажите название курса",
    )
    preview = models.ImageField(
        upload_to="courses/previews",
        blank=True,
        null=True,
        verbose_name="Превью",
        help_text="Загрузите изображение курса",
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание",
        help_text="Введите описание курса",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Цена",
        help_text="Укажите цену курса",
    )

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"


class Lessons(models.Model):
    title = models.CharField(
        max_length=255,
        verbose_name="Название",
        help_text="Укажите название урока",
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание",
        help_text="Введите описание урока",
    )
    preview = models.ImageField(
        upload_to="lessons/previews",
        blank=True,
        null=True,
        verbose_name="Превью",
        help_text="Загрузите изображение урока",
    )
    video_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Ссылка на видео",
        help_text="Введите ссылку на видеоурок",
    )
    course = models.ForeignKey(
        Course,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Курс",
        help_text="Выберите курс, к которому относится урок",
    )
    owner = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="lessons",
        null=True,
        blank=True,
        verbose_name="Владелец",
        help_text="Укажите владельца урока",
    )

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"


class Subscription(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} подписан на {self.course.title}"

    class Meta:
        unique_together = ("user", "course")
