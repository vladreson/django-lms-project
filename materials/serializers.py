from rest_framework import serializers
from .models import Course, Lesson, Subscription
from .validators import validate_youtube_url


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для подписок
    """
    user_email = serializers.EmailField(source='user.email', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = Subscription
        fields = ['id', 'user', 'user_email', 'course', 'course_title', 'subscribed_at']
        read_only_fields = ['id', 'subscribed_at']


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Lesson.objects.all(),
                fields=['title', 'course'],
                message='Урок с таким названием уже существует в этом курсе'
            )
        ]

    def validate_video_url(self, value):
        """
        Валидация поля video_url
        """
        if value:
            validate_youtube_url(value)
        return value


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True, source='lessons.all')
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        """
        Проверяет подписан ли текущий пользователь на курс
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.subscriptions.filter(user=request.user).exists()
        return False