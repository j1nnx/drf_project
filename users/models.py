from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = None
    email = models.EmailField(
        unique=True, verbose_name="Почта", help_text="Укажите почту"
    )
    phone = models.CharField(
        max_length=35,
        blank=True,
        null=True,
        verbose_name="Телефон",
        help_text="Укажите телефон",
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Город",
        help_text="Укажите город",
    )
    avatar = models.ImageField(
        upload_to="users/avatars",
        blank=True,
        null=True,
        verbose_name="Аватарка",
        help_text="Загрузите аватарку",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Payments(models.Model):
    PAYMENT_STATUS = [
        ("cash", "наличные"),
        ("transfer", "перевод на счет"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user", verbose_name="Пользователь"
    )
    payment_date = models.DateField(null=True, blank=True, verbose_name="Дата оплаты")
    paid_course = models.ForeignKey(
        "course.Course",
        on_delete=models.CASCADE,
        related_name="course",
        verbose_name="Оплаченный курс",
        null=True,
        blank=True,
    )
    separately_paid_lesson = models.ForeignKey(
        "course.Lessons",
        on_delete=models.CASCADE,
        related_name="lesson",
        verbose_name="Оплаченный урок",
        null=True,
        blank=True,
    )
    payment_amount = models.IntegerField(
        default=0, verbose_name="Сумма оплаты", null=True, blank=True
    )
    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS,
        default="cash",
        verbose_name="Способ оплаты",
        null=True,
        blank=True,
    )
    stripe_session_id = models.CharField(
        max_length=400,
        null=True,
        blank=True,
        verbose_name="ID сессии Stripe"
    )
    stripe_status = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="Статус оплаты в Stripe"
    )

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
