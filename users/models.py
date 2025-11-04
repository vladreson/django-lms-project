from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name='Email')
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name='Телефон')
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name='Город')
    avatar = models.ImageField(upload_to='users/avatars/', blank=True, null=True, verbose_name='Аватар')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Наличные'),
        ('transfer', 'Перевод на счет'),
        ('stripe', 'Stripe'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('processing', 'В обработке'),
        ('succeeded', 'Оплачено'),
        ('failed', 'Ошибка оплаты'),
        ('canceled', 'Отменено'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='Пользователь'
    )
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата оплаты')

    paid_course = models.ForeignKey(
        'materials.Course',
        on_delete=models.CASCADE,
        related_name='payments',
        blank=True,
        null=True,
        verbose_name='Оплаченный курс'
    )
    paid_lesson = models.ForeignKey(
        'materials.Lesson',
        on_delete=models.CASCADE,
        related_name='payments',
        blank=True,
        null=True,
        verbose_name='Оплаченный урок'
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Сумма оплаты'
    )
    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name='Способ оплаты'
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending',
        verbose_name='Статус оплаты'
    )
    stripe_product_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='ID продукта в Stripe'
    )
    stripe_price_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='ID цены в Stripe'
    )
    stripe_session_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='ID сессии в Stripe'
    )
    stripe_payment_intent_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='ID платежа в Stripe'
    )

    def __str__(self):
        payment_for = self.paid_course if self.paid_course else self.paid_lesson
        return f"{self.user.email} - {payment_for} - {self.amount}"

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        ordering = ['-payment_date']