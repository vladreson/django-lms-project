from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from materials.views import CourseViewSet
from users.views import UserViewSet, PaymentViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'users', UserViewSet)
router.register(r'payments', PaymentViewSet)

def api_root(request):
    return JsonResponse({
        'message': 'Django LMS API',
        'endpoints': {
            'courses': '/api/courses/',
            'lessons': '/api/lessons/',
            'users': '/api/users/',
            'payments': '/api/payments/',
            'admin': '/admin/'
        }
    })

urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/lessons/', include('materials.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)