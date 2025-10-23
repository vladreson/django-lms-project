from django.urls import path
from .views import LessonListCreateAPIView, LessonRetrieveUpdateDestroyAPIView

urlpatterns = [
    path('', LessonListCreateAPIView.as_view(), name='lesson-list-create'),
    path('<int:pk>/', LessonRetrieveUpdateDestroyAPIView.as_view(), name='lesson-detail'),
]