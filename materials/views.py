from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Course, Lesson, Subscription
from .serializers import CourseSerializer, LessonSerializer, SubscriptionSerializer
from users.permissions import IsModerator, IsOwner, IsOwnerOrModerator, IsNotModerator
from .paginators import MaterialsPaginator, SubscriptionPaginator
from .tasks import send_course_update_notification


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления курсами.
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = MaterialsPaginator

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsNotModerator()]
        elif self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), IsOwnerOrModerator()]
        elif self.action == 'destroy':
            return [IsAuthenticated(), IsOwner()]
        elif self.action == 'retrieve':
            return [IsAuthenticated()]
        else:
            return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='moderators').exists():
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    def update(self, request, *args, **kwargs):
        """
        Переопределяем update для отправки уведомлений об обновлении курса
        """
        course = self.get_object()
        last_updated = course.updated_at

        # Выполняем обновление
        response = super().update(request, *args, **kwargs)

        # Проверяем, что курс действительно обновлен
        course.refresh_from_db()

        # Отправляем уведомление если курс обновлен и прошло более 4 часов с последнего обновления
        if last_updated:
            time_diff = timezone.now() - last_updated
            if time_diff > timedelta(hours=4):
                # Отправляем уведомление асинхронно
                send_course_update_notification.delay(course.id)
                print(f"Запущена задача отправки уведомлений для курса {course.id}")
        else:
            # Если нет информации о последнем обновлении, отправляем уведомление
            send_course_update_notification.delay(course.id)

        return response

    def partial_update(self, request, *args, **kwargs):
        """
        Переопределяем partial_update для отправки уведомлений
        """
        course = self.get_object()
        last_updated = course.updated_at

        response = super().partial_update(request, *args, **kwargs)

        course.refresh_from_db()

        if last_updated:
            time_diff = timezone.now() - last_updated
            if time_diff > timedelta(hours=4):
                send_course_update_notification.delay(course.id)
                print(f"Запущена задача отправки уведомлений для курса {course.id}")
        else:
            send_course_update_notification.delay(course.id)

        return response

    @swagger_auto_schema(
        method='get',
        operation_description="Получить список уроков курса",
        responses={200: LessonSerializer(many=True), 403: 'Доступ запрещен'}
    )
    @action(detail=True, methods=['get'])
    def lessons(self, request, pk=None):
        course = self.get_object()
        lessons = course.lessons.all()

        user = self.request.user
        if not user.groups.filter(name='moderators').exists() and course.owner != user:
            return Response({"detail": "У вас нет прав для просмотра этих уроков"}, status=403)

        paginator = MaterialsPaginator()
        paginated_lessons = paginator.paginate_queryset(lessons, request)
        serializer = LessonSerializer(paginated_lessons, many=True)
        return paginator.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        method='post',
        operation_description="Подписаться на курс",
        responses={
            201: 'Подписка создана',
            400: 'Уже подписан на курс'
        }
    )
    @swagger_auto_schema(
        method='delete',
        operation_description="Отписаться от курса",
        responses={
            200: 'Отписка выполнена',
            400: 'Не подписан на курс'
        }
    )
    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk=None):
        course = self.get_object()
        user = request.user

        if request.method == 'POST':
            subscription, created = Subscription.objects.get_or_create(
                user=user,
                course=course
            )
            if created:
                return Response(
                    {"message": f"Вы подписались на курс '{course.title}'"},
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {"message": "Вы уже подписаны на этот курс"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        elif request.method == 'DELETE':
            deleted_count, _ = Subscription.objects.filter(
                user=user,
                course=course
            ).delete()

            if deleted_count:
                return Response(
                    {"message": f"Вы отписались от курса '{course.title}'"},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"message": "Вы не подписаны на этот курс"},
                    status=status.HTTP_400_BAD_REQUEST
                )


# Остальные классы представлений остаются без изменений
class LessonListCreateAPIView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['course']
    pagination_class = MaterialsPaginator

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsNotModerator()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)


class LessonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH']:
            return [IsAuthenticated(), IsOwnerOrModerator()]
        elif self.request.method == 'DELETE':
            return [IsAuthenticated(), IsOwner()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)


class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = SubscriptionPaginator

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)