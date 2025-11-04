from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from materials.views import CourseViewSet, LessonListCreateAPIView, LessonRetrieveUpdateDestroyAPIView, \
    SubscriptionViewSet
from users.views import UserViewSet, PaymentViewSet, UserRegisterAPIView, PaymentSuccessAPIView, PaymentCancelAPIView, \
    CheckPaymentStatusAPIView

# Настройки для Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="LMS API",
        default_version='v1',
        description="API для системы управления обучением (LMS)",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="admin@lms.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


def api_root(request):
    return JsonResponse({
        'message': 'Django LMS API',
        'endpoints': {
            'register': '/api/register/',
            'token': '/api/token/',
            'token_refresh': '/api/token/refresh/',
            'courses': '/api/courses/',
            'lessons': '/api/lessons/',
            'users': '/api/users/',
            'payments': '/api/payments/',
            'subscriptions': '/api/subscriptions/',
            'admin': '/admin/',
            'swagger': '/swagger/',
            'redoc': '/redoc/',
        }
    })


urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),

    # Документация
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Аутентификация
    path('api/register/', UserRegisterAPIView.as_view(), name='register'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Платежи
    path('api/payments/success/', PaymentSuccessAPIView.as_view(), name='payment-success'),
    path('api/payments/cancel/', PaymentCancelAPIView.as_view(), name='payment-cancel'),
    path('api/payments/<int:payment_id>/status/', CheckPaymentStatusAPIView.as_view(), name='payment-status'),

    # API
    path('api/courses/', CourseViewSet.as_view({'get': 'list', 'post': 'create'}), name='course-list'),
    path('api/courses/<int:pk>/', CourseViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
    }), name='course-detail'),
    path('api/courses/<int:pk>/lessons/', CourseViewSet.as_view({'get': 'lessons'}), name='course-lessons'),
    path('api/courses/<int:pk>/subscribe/', CourseViewSet.as_view({'post': 'subscribe', 'delete': 'subscribe'}),
         name='course-subscribe'),

    path('api/lessons/', LessonListCreateAPIView.as_view(), name='lesson-list-create'),
    path('api/lessons/<int:pk>/', LessonRetrieveUpdateDestroyAPIView.as_view(), name='lesson-detail'),

    path('api/users/', UserViewSet.as_view({'get': 'list', 'post': 'create'}), name='user-list'),
    path('api/users/<int:pk>/', UserViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
    }), name='user-detail'),

    path('api/payments/', PaymentViewSet.as_view({'get': 'list', 'post': 'create'}), name='payment-list'),
    path('api/payments/create-stripe-payment/', PaymentViewSet.as_view({'post': 'create_stripe_payment'}),
         name='create-stripe-payment'),
    path('api/payments/<int:pk>/', PaymentViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
    }), name='payment-detail'),

    path('api/subscriptions/', SubscriptionViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='subscription-list'),
    path('api/subscriptions/<int:pk>/', SubscriptionViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
    }), name='subscription-detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)