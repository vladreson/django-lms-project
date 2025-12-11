import stripe
from django.conf import settings
from django.urls import reverse

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """
    Сервис для работы с Stripe API
    """

    @staticmethod
    def create_product(name, description=None):
        """
        Создание продукта в Stripe
        """
        try:
            product = stripe.Product.create(
                name=name,
                description=description,
            )
            return product
        except stripe.error.StripeError as e:
            raise Exception(f"Ошибка создания продукта в Stripe: {str(e)}")

    @staticmethod
    def create_price(product_id, amount, currency='rub'):
        """
        Создание цены в Stripe

        Args:
            product_id: ID продукта в Stripe
            amount: Сумма в рублях (умножается на 100 для копеек)
            currency: Валюта (по умолчанию RUB)
        """
        try:
            # Stripe ожидает сумму в копейках для RUB
            amount_in_cents = int(amount * 100)

            price = stripe.Price.create(
                product=product_id,
                unit_amount=amount_in_cents,
                currency=currency,
            )
            return price
        except stripe.error.StripeError as e:
            raise Exception(f"Ошибка создания цены в Stripe: {str(e)}")

    @staticmethod
    def create_checkout_session(price_id, success_url, cancel_url, metadata=None):
        """
        Создание сессии для оплаты в Stripe
        """
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=metadata or {},
            )
            return session
        except stripe.error.StripeError as e:
            raise Exception(f"Ошибка создания сессии в Stripe: {str(e)}")

    @staticmethod
    def retrieve_session(session_id):
        """
        Получение информации о сессии
        """
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            return session
        except stripe.error.StripeError as e:
            raise Exception(f"Ошибка получения сессии из Stripe: {str(e)}")

    @staticmethod
    def create_payment_for_course(course, user, base_url):
        """
        Создание платежа для курса в Stripe
        """
        try:
            # Создаем продукт в Stripe
            product = StripeService.create_product(
                name=course.title,
                description=course.description
            )

            # Создаем цену в Stripe
            price = StripeService.create_price(
                product_id=product.id,
                amount=course.price if hasattr(course, 'price') else 1000  # Заглушка цены
            )

            # Создаем URL для успешной оплаты и отмены
            success_url = f"{base_url}{reverse('payment-success')}?session_id={{CHECKOUT_SESSION_ID}}"
            cancel_url = f"{base_url}{reverse('payment-cancel')}"

            # Создаем сессию оплаты
            session = StripeService.create_checkout_session(
                price_id=price.id,
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'course_id': str(course.id),
                    'user_id': str(user.id)
                }
            )

            return {
                'product_id': product.id,
                'price_id': price.id,
                'session_id': session.id,
                'payment_url': session.url
            }

        except Exception as e:
            raise Exception(f"Ошибка создания платежа: {str(e)}")