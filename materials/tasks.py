from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Course, Subscription


@shared_task
def send_course_update_notification(course_id):
    """
    Задача для отправки уведомлений об обновлении курса подписанным пользователям.
    """
    try:
        course = Course.objects.get(id=course_id)
        subscriptions = Subscription.objects.filter(course=course).select_related('user')

        if not subscriptions:
            print(f"Нет подписчиков для курса: {course.title}")
            return

        subject = f'Обновление курса "{course.title}"'
        message = f'Дорогой пользователь!\n\nКурс "{course.title}" был обновлен. Проверьте новые материалы!\n\nС уважением, команда LMS'

        recipient_list = [subscription.user.email for subscription in subscriptions]

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )

        print(f"Уведомления отправлены {len(recipient_list)} подписчикам курса '{course.title}'")

    except Course.DoesNotExist:
        print(f"Курс с id {course_id} не найден")
    except Exception as e:
        print(f"Ошибка при отправке уведомления: {str(e)}")


@shared_task
def check_course_updates():
    """
    Периодическая задача для проверки обновлений курсов за последние 4 часа
    и отправки уведомлений подписчикам.
    """
    four_hours_ago = timezone.now() - timedelta(hours=4)

    # Находим курсы, обновленные за последние 4 часа
    updated_courses = Course.objects.filter(updated_at__gte=four_hours_ago)

    for course in updated_courses:
        # Отправляем уведомление для каждого обновленного курса
        send_course_update_notification.delay(course.id)

    print(f"Проверены обновления для {updated_courses.count()} курсов")