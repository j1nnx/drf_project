import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_API_KEY


def create_stripe_product(course):
    """Создает продукт в Stripe на основе курса."""
    try:
        product = stripe.Product.create(
            name=course.title,
            description=course.description or f"Курс: {course.title}",
        )
        return product
    except stripe.error.StripeError as e:
        raise Exception(f"Ошибка при создании продукта: {str(e)}")


def create_stripe_price(amount, product_id, currency="rub"):
    """Создает цену для продукта в Stripe."""
    try:
        price = stripe.Price.create(
            unit_amount=int(amount * 100),
            currency=currency,
            product=product_id,
        )
        return price
    except stripe.error.StripeError as e:
        raise Exception(f"Ошибка при создании цены: {str(e)}")


def create_stripe_session(price_id, success_url, cancel_url, course_id, user_id):
    """Создает сессию оплаты в Stripe."""
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=f"{success_url}?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=cancel_url,
            metadata={
                "course_id": course_id,
                "user_id": user_id,
            }
        )
        return session.id, session.url
    except stripe.error.StripeError as e:
        raise Exception(f"Ошибка при создании сессии: {str(e)}")
