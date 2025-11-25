import stripe
from django.conf import settings
from .gateway import PaymentGateway

stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeGateway(PaymentGateway):
    def initiate_payment(self, amount, member):
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'ugx',
                    'product_data': {'name': 'SACCO Contribution'},
                    'unit_amount': int(amount * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=settings.STRIPE_SUCCESS_URL,
            cancel_url=settings.STRIPE_CANCEL_URL,
            metadata={'member_id': member.id}
        )
        return session.url, session.id

    def verify_payment(self, payload):
        event = stripe.Event.construct_from(
            payload, stripe.api_key
        )
        return event
