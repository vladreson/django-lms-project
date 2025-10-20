from django_filters import rest_framework as filters
from .models import Payment


class PaymentFilter(filters.FilterSet):
    payment_date = filters.DateFromToRangeFilter(field_name='payment_date')
    course = filters.ModelChoiceFilter(
        field_name='paid_course',
        queryset=lambda request: Payment.objects.filter(paid_course__isnull=False).values_list('paid_course',
                                                                                               flat=True).distinct()
    )
    lesson = filters.ModelChoiceFilter(
        field_name='paid_lesson',
        queryset=lambda request: Payment.objects.filter(paid_lesson__isnull=False).values_list('paid_lesson',
                                                                                               flat=True).distinct()
    )
    payment_method = filters.ChoiceFilter(choices=Payment.PAYMENT_METHOD_CHOICES)

    ordering = filters.OrderingFilter(
        fields=(
            ('payment_date', 'payment_date'),
            ('amount', 'amount'),
        ),
        field_labels={
            'payment_date': 'Дата оплаты',
            'amount': 'Сумма оплаты',
        }
    )

    class Meta:
        model = Payment
        fields = ['payment_date', 'course', 'lesson', 'payment_method']