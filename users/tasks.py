from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

User = get_user_model()


@shared_task
def block_inactive_users():
    """
    Периодическая задача для блокировки пользователей,
    которые не заходили более месяца.
    """
    one_month_ago = timezone.now() - timedelta(days=30)

    # Находим активных пользователей, которые не заходили более месяца
    inactive_users = User.objects.filter(
        last_login__lt=one_month_ago,
        is_active=True
    )

    user_count = inactive_users.count()

    # Блокируем пользователей
    inactive_users.update(is_active=False)

    print(f"Заблокировано {user_count} неактивных пользователей")

    return user_count


@shared_task
def send_welcome_email(user_id):
    """
    Задача для отправки приветственного письма новому пользователю.
    """
    try:
        user = User.objects.get(id=user_id)

        subject = 'Добро пожаловать в LMS!'
        message = f'''Добро пожаловать, {user.first_name or 'пользователь'}!

Благодарим за регистрацию в нашей системе обучения.

С уважением,
Команда LMS'''

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        print(f"Приветственное письмо отправлено пользователю {user.email}")

    except User.DoesNotExist:
        print(f"Пользователь с id {user_id} не найден")