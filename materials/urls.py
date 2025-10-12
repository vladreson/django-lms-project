from django.urls import path
from .views import (
    LessonListCreateAPIView,
    LessonRetrieveAPIView,
    LessonUpdateAPIView,
    LessonDestroyAPIView
)

urlpatterns = [
    path('', LessonListCreateAPIView.as_view(), name='lesson-list'),
    path('<int:pk>/', LessonRetrieveAPIView.as_view(), name='lesson-detail'),
    path('<int:pk>/update/', LessonUpdateAPIView.as_view(), name='lesson-update'),
    path('<int:pk>/delete/', LessonDestroyAPIView.as_view(), name='lesson-delete'),
]