from rest_framework import viewsets, generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django_filters import rest_framework as filters
from django.conf import settings
from django.urls import reverse
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Payment, User
from .serializers import PaymentSerializer, UserSerializer, UserRegisterSerializer, PaymentCreateSerializer
from .filters import PaymentFilter
from .services.stripe_service import StripeService
from .tasks import send_welcome_email


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления пользователями.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]


class UserRegisterAPIView(generics.CreateAPIView):
    """
    Регистрация нового пользователя.
    """
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Регистрация нового пользователя",
        responses={
            201: openapi.Response('Пользователь создан', UserRegisterSerializer),
            400: 'Неверные данные'
        }
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        # Если пользователь успешно создан, отправляем приветственное письмо
        if response.status_code == status.HTTP_201_CREATED:
            user_id = response.data.get('user', {}).get('id')
            if user_id:
                send_welcome_email.delay(user_id)

        return response


# Остальные классы представлений остаются без изменений
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = PaymentFilter
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        return PaymentSerializer

    @swagger_auto_schema(
        method='post',
        operation_description="Создать платеж через Stripe для курса",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'course_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID курса'),
            },
            required=['course_id']
        ),
        responses={
            201: openapi.Response('Платеж создан', PaymentSerializer),
            400: 'Неверные данные',
            404: 'Курс не найден'
        }
    )
    @action(detail=False, methods=['post'], url_path='create-stripe-payment')
    def create_stripe_payment(self, request):
        from materials.models import Course

        course_id = request.data.get('course_id')

        if not course_id:
            return Response(
                {"error": "course_id обязателен"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response(
                {"error": "Курс не найден"},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            base_url = getattr(settings, 'FRONTEND_URL', request.build_absolute_uri('/'))

            stripe_data = StripeService.create_payment_for_course(
                course=course,
                user=request.user,
                base_url=base_url
            )

            payment = Payment.objects.create(
                user=request.user,
                paid_course=course,
                amount=course.price if hasattr(course, 'price') else 1000,
                payment_method='stripe',
                payment_status='pending',
                stripe_product_id=stripe_data['product_id'],
                stripe_price_id=stripe_data['price_id'],
                stripe_session_id=stripe_data['session_id']
            )

            serializer = PaymentSerializer(payment)

            return Response({
                "payment": serializer.data,
                "payment_url": stripe_data['payment_url']
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class PaymentSuccessAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        session_id = request.GET.get('session_id')

        if not session_id:
            return Response(
                {"error": "session_id обязателен"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            session = StripeService.retrieve_session(session_id)

            if session.payment_status == 'paid':
                try:
                    payment = Payment.objects.get(stripe_session_id=session_id)
                    payment.payment_status = 'succeeded'
                    payment.stripe_payment_intent_id = session.payment_intent
                    payment.save()

                    return Response({
                        "message": "Оплата прошла успешно",
                        "payment": PaymentSerializer(payment).data
                    })

                except Payment.DoesNotExist:
                    return Response(
                        {"error": "Платеж не найден"},
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                return Response(
                    {"error": "Платеж не завершен"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class PaymentCancelAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "message": "Оплата отменена. Вы можете повторить попытку позже."
        })


class CheckPaymentStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, payment_id):
        try:
            payment = Payment.objects.get(id=payment_id, user=request.user)

            if payment.payment_method == 'stripe' and payment.stripe_session_id:
                session = StripeService.retrieve_session(payment.stripe_session_id)

                if session.payment_status == 'paid' and payment.payment_status != 'succeeded':
                    payment.payment_status = 'succeeded'
                    payment.stripe_payment_intent_id = session.payment_intent
                    payment.save()

            serializer = PaymentSerializer(payment)
            return Response(serializer.data)

        except Payment.DoesNotExist:
            return Response(
                {"error": "Платеж не найден"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )