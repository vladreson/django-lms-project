from rest_framework import viewsets
from django_filters import rest_framework as filters
from .models import Payment, User
from .serializers import PaymentSerializer, UserSerializer
from .filters import PaymentFilter


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = PaymentFilter