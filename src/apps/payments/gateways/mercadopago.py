import mercadopago
from django.conf import settings
from .base import BaseGateway

STATUS_MAP = {
    'approved': 'approved',
    'pending': 'pending',
    'in_process': 'in_process',
    'rejected': 'rejected',
    'cancelled': 'cancelled',
    'refunded': 'refunded',
    'charged_back': 'refunded',
}


class MercadoPagoGateway(BaseGateway):

    def __init__(self):
        self.sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN)

    def create_preference(self, order):
        items = []
        for item in order.items.select_related('course'):
            items.append({
                'id': str(item.course.id) if item.course else 'curso',
                'title': item.course_title,
                'quantity': 1,
                'unit_price': float(item.unit_price),
                'currency_id': 'BRL',
            })

        back_urls = {
            'success': f'{settings.SITE_URL}/pagamentos/sucesso/',
            'pending': f'{settings.SITE_URL}/pagamentos/pendente/',
            'failure': f'{settings.SITE_URL}/pagamentos/falha/',
        }

        preference_data = {
            'items': items,
            'payer': {
                'name': order.customer_name,
                'email': order.customer_email,
                'identification': {
                    'type': 'CPF',
                    'number': order.customer_cpf.replace('.', '').replace('-', ''),
                },
            },
            'back_urls': back_urls,
            'auto_return': 'approved',
            'external_reference': order.number,
            'notification_url': f'{settings.SITE_URL}/pagamentos/webhook/mercadopago/',
            'payment_methods': {
                'installments': 12,
            },
            'statement_descriptor': 'FG CURSOS',
        }

        response = self.sdk.preference().create(preference_data)
        preference = response.get('response', {})

        return {
            'preference_id': preference.get('id', ''),
            'init_point': preference.get('init_point', ''),
            'sandbox_init_point': preference.get('sandbox_init_point', ''),
            'raw': preference,
        }

    def get_payment(self, payment_id):
        response = self.sdk.payment().get(payment_id)
        payment_data = response.get('response', {})

        return {
            'id': str(payment_data.get('id', '')),
            'status': payment_data.get('status', 'pending'),
            'payment_method_id': payment_data.get('payment_method_id', ''),
            'external_reference': payment_data.get('external_reference', ''),
            'raw': payment_data,
        }

    def normalize_status(self, gateway_status):
        return STATUS_MAP.get(gateway_status, 'pending')
