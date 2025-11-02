from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LessonListCreateAPIView, LessonRetrieveUpdateDestroyAPIView, SubscriptionViewSet

router = DefaultRouter()
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')

urlpatterns = [
    path('', LessonListCreateAPIView.as_view(), name='lesson-list-create'),
    path('<int:pk>/', LessonRetrieveUpdateDestroyAPIView.as_view(), name='lesson-detail'),
    path('', include(router.urls)),
]