from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from materials.views import CourseViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet)

def api_root(request):
    return JsonResponse({
        'message': 'Django LMS API',
        'endpoints': {
            'courses': '/api/courses/',
            'lessons': '/api/lessons/',
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