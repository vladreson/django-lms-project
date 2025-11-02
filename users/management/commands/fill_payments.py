import os
import django
from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import User, Payment
from materials.models import Course, Lesson
from decimal import Decimal


class Command(BaseCommand):
    help = 'Fill database with sample payment data'

    def handle(self, *args, **options):
        # Создаем тестового пользователя если нет
        user, created = User.objects.get_or_create(
            email='testuser@example.com',
            defaults={
                'first_name': 'Test',
                'last_name': 'User',
                'is_staff': False,
                'is_active': True
            }
        )
        if created:
            user.set_password('12345')
            user.save()
            self.stdout.write(self.style.SUCCESS('Created test user'))

        # Получаем или создаем курсы и уроки
        course1, _ = Course.objects.get_or_create(
            title='Python для начинающих',
            defaults={'description': 'Базовый курс по Python'}
        )

        course2, _ = Course.objects.get_or_create(
            title='Django Framework',
            defaults={'description': 'Изучение веб-фреймворка Django'}
        )

        lesson1, _ = Lesson.objects.get_or_create(
            title='Введение в Python',
            defaults={
                'description': 'Основы языка Python',
                'course': course1,
                'video_url': 'https://example.com/python-intro'
            }
        )

        lesson2, _ = Lesson.objects.get_or_create(
            title='Модели в Django',
            defaults={
                'description': 'Работа с моделями Django',
                'course': course2,
                'video_url': 'https://example.com/django-models'
            }
        )

        # Создаем платежи
        payments_data = [
            {
                'user': user,
                'paid_course': course1,
                'paid_lesson': None,
                'amount': Decimal('15000.00'),
                'payment_method': 'transfer'
            },
            {
                'user': user,
                'paid_course': None,
                'paid_lesson': lesson1,
                'amount': Decimal('2000.00'),
                'payment_method': 'cash'
            },
            {
                'user': user,
                'paid_course': course2,
                'paid_lesson': None,
                'amount': Decimal('18000.00'),
                'payment_method': 'transfer'
            },
            {
                'user': user,
                'paid_course': None,
                'paid_lesson': lesson2,
                'amount': Decimal('2500.00'),
                'payment_method': 'cash'
            },
        ]

        created_count = 0
        for payment_data in payments_data:
            payment, created = Payment.objects.get_or_create(
                user=payment_data['user'],
                paid_course=payment_data['paid_course'],
                paid_lesson=payment_data['paid_lesson'],
                defaults={
                    'amount': payment_data['amount'],
                    'payment_method': payment_data['payment_method']
                }
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} payments')
        )