from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from users.models import User
from .models import Course, Lesson, Subscription
from .validators import validate_youtube_url
from django.core.exceptions import ValidationError


class LessonTestCase(APITestCase):
    """
    Тесты для CRUD операций с уроками
    """

    def setUp(self):
        # Создаем пользователей
        self.regular_user = User.objects.create_user(
            email='regular@example.com',
            password='testpass123'
        )
        self.moderator_user = User.objects.create_user(
            email='moderator@example.com',
            password='testpass123'
        )

        # Создаем группу модераторов и добавляем пользователя
        from django.contrib.auth.models import Group
        moderators_group, _ = Group.objects.get_or_create(name='moderators')
        self.moderator_user.groups.add(moderators_group)

        # Создаем курс
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            owner=self.regular_user
        )

        # Создаем урок
        self.lesson = Lesson.objects.create(
            title='Test Lesson',
            description='Test Lesson Description',
            video_url='https://www.youtube.com/watch?v=test123',
            course=self.course,
            owner=self.regular_user
        )

        # URL для тестов
        self.lessons_list_url = reverse('lesson-list-create')
        self.lesson_detail_url = reverse('lesson-detail', kwargs={'pk': self.lesson.pk})

    def test_lesson_list_authenticated(self):
        """Тест получения списка уроков аутентифицированным пользователем"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.lessons_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_lesson_list_unauthenticated(self):
        """Тест получения списка уроков неаутентифицированным пользователем"""
        response = self.client.get(self.lessons_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_lesson_create_regular_user(self):
        """Тест создания урока обычным пользователем"""
        self.client.force_authenticate(user=self.regular_user)
        data = {
            'title': 'New Lesson',
            'description': 'New Lesson Description',
            'video_url': 'https://www.youtube.com/watch?v=new123',
            'course': self.course.id
        }
        response = self.client.post(self.lessons_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_lesson_create_moderator(self):
        """Тест что модератор не может создать урок"""
        self.client.force_authenticate(user=self.moderator_user)
        data = {
            'title': 'Moderator Lesson',
            'description': 'Moderator Lesson Description',
            'video_url': 'https://www.youtube.com/watch?v=mod123',
            'course': self.course.id
        }
        response = self.client.post(self.lessons_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_update_owner(self):
        """Тест обновления урока владельцем"""
        self.client.force_authenticate(user=self.regular_user)
        data = {
            'title': 'Updated Lesson',
            'description': 'Updated Description',
            'video_url': 'https://www.youtube.com/watch?v=updated123',
            'course': self.course.id
        }
        response = self.client.put(self.lesson_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Updated Lesson')

    def test_lesson_update_moderator(self):
        """Тест обновления урока модератором"""
        self.client.force_authenticate(user=self.moderator_user)
        data = {
            'title': 'Moderator Updated',
        }
        response = self.client.patch(self.lesson_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Moderator Updated')

    def test_lesson_delete_owner(self):
        """Тест удаления урока владельцем"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.delete(self.lesson_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_lesson_delete_moderator(self):
        """Тест что модератор не может удалить урок"""
        self.client.force_authenticate(user=self.moderator_user)
        response = self.client.delete(self.lesson_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class SubscriptionTestCase(APITestCase):
    """
    Тесты для функционала подписок
    """

    def setUp(self):
        # Создаем пользователя
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpass123'
        )

        # Создаем курс
        self.course = Course.objects.create(
            title='Test Course for Subscription',
            description='Test Description',
            owner=self.user
        )

        # URL для тестов подписки
        self.subscribe_url = f'/api/courses/{self.course.id}/subscribe/'

    def test_subscribe_to_course(self):
        """Тест подписки на курс"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.subscribe_url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_unsubscribe_from_course(self):
        """Тест отписки от курса"""
        # Сначала подписываемся
        Subscription.objects.create(user=self.user, course=self.course)

        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.subscribe_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_subscribe_already_subscribed(self):
        """Тест повторной подписки на курс"""
        Subscription.objects.create(user=self.user, course=self.course)

        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.subscribe_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsubscribe_not_subscribed(self):
        """Тест отписки когда не подписан"""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.subscribe_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ValidatorTestCase(TestCase):
    """
    Тесты для валидаторов
    """

    def test_valid_youtube_url(self):
        """Тест валидных YouTube ссылок"""
        valid_urls = [
            'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            'https://youtube.com/watch?v=test123',
            'https://youtu.be/dQw4w9WgXcQ',
            'http://www.youtube.com/watch?v=test123',
        ]

        for url in valid_urls:
            try:
                validate_youtube_url(url)
            except ValidationError:
                self.fail(f"validate_youtube_url raised ValidationError for valid URL: {url}")

    def test_invalid_youtube_url(self):
        """Тест невалидных YouTube ссылок"""
        invalid_urls = [
            'https://vimeo.com/123456',
            'https://example.com/video',
            'https://rutube.ru/video/123',
            'not-a-url',
        ]

        for url in invalid_urls:
            with self.assertRaises(ValidationError):
                validate_youtube_url(url)


class PaginationTestCase(APITestCase):
    """
    Тесты для пагинации
    """

    def setUp(self):
        self.user = User.objects.create_user(
            email='pagination@example.com',
            password='testpass123'
        )

        # Создаем несколько курсов для тестирования пагинации
        for i in range(15):
            Course.objects.create(
                title=f'Course {i}',
                description=f'Description {i}',
                owner=self.user
            )

        self.courses_list_url = reverse('course-list')

    def test_pagination_default(self):
        """Тест пагинации по умолчанию"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.courses_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 10)  # page_size по умолчанию

    def test_pagination_custom_page_size(self):
        """Тест пагинации с кастомным размером страницы"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"{self.courses_list_url}?page_size=5")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)

    def test_pagination_max_page_size(self):
        """Тест максимального размера страницы"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"{self.courses_list_url}?page_size=100")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 15)  # Всего 15 элементов