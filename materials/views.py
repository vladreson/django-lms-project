from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from .models import Course, Lesson, Subscription
from .serializers import CourseSerializer, LessonSerializer, SubscriptionSerializer
from users.permissions import IsModerator, IsOwner, IsOwnerOrModerator, IsNotModerator
from .paginators import MaterialsPaginator, SubscriptionPaginator


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления подписками
    """
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = SubscriptionPaginator

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = MaterialsPaginator

    def get_permissions(self):
        """
        Простая и понятная система прав без сложных операторов
        """
        if self.action == 'create':
            # Создавать могут только аутентифицированные пользователи, которые НЕ модераторы
            return [IsAuthenticated(), IsNotModerator()]
        elif self.action in ['update', 'partial_update']:
            # Обновлять могут модераторы ИЛИ владельцы
            return [IsAuthenticated(), IsOwnerOrModerator()]
        elif self.action == 'destroy':
            # Удалять могут только владельцы
            return [IsAuthenticated(), IsOwner()]
        elif self.action == 'retrieve':
            # Просматривать детали могут все аутентифицированные
            return [IsAuthenticated()]
        else:
            # По умолчанию - все аутентифицированные
            return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='moderators').exists():
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    @action(detail=True, methods=['get'])
    def lessons(self, request, pk=None):
        course = self.get_object()
        lessons = course.lessons.all()

        # Проверка прав доступа к урокам
        user = self.request.user
        if not user.groups.filter(name='moderators').exists() and course.owner != user:
            return Response({"detail": "У вас нет прав для просмотра этих уроков"}, status=403)

        # Пагинация для уроков
        paginator = MaterialsPaginator()
        paginated_lessons = paginator.paginate_queryset(lessons, request)
        serializer = LessonSerializer(paginated_lessons, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk=None):
        """
        Эндпоинт для подписки/отписки на курс
        """
        course = self.get_object()
        user = request.user

        if request.method == 'POST':
            # Подписка
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
            # Отписка
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