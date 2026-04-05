import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def process_payment_notification(self, mp_payment_id):
    """
    Consulta o Mercado Pago e atualiza o status do pagamento e do pedido.
    Reenfileira em caso de falha (até 5 tentativas com intervalo de 60s).
    """
    from .models import Payment
    from .gateways.mercadopago import MercadoPagoGateway
    from apps.orders.models import Order

    try:
        gateway = MercadoPagoGateway()
        payment_data = gateway.get_payment(mp_payment_id)

        order_number = payment_data.get('external_reference', '')
        if not order_number:
            logger.warning(f'Webhook sem external_reference para payment_id={mp_payment_id}')
            return

        try:
            order = Order.objects.get(number=order_number)
        except Order.DoesNotExist:
            logger.error(f'Pedido não encontrado: {order_number}')
            return

        normalized_status = gateway.normalize_status(payment_data['status'])

        # Atualiza ou cria o registro de pagamento
        payment, _ = Payment.objects.update_or_create(
            order=order,
            gateway=Payment.GATEWAY_MERCADOPAGO,
            gateway_payment_id=str(mp_payment_id),
            defaults={
                'status': normalized_status,
                'payment_method': payment_data.get('payment_method_id', ''),
                'amount': order.total,
                'raw_response': payment_data.get('raw', {}),
            }
        )

        if normalized_status == Payment.STATUS_APPROVED and order.status != Order.STATUS_PAID:
            logger.info(f'Confirmando pedido {order_number} após aprovação do MP.')
            order.confirm()
            send_enrollment_confirmation_email.delay(order.id)

        elif normalized_status in (Payment.STATUS_REJECTED, Payment.STATUS_CANCELLED):
            order.status = Order.STATUS_FAILED
            order.save(update_fields=['status', 'updated_at'])
            logger.info(f'Pedido {order_number} marcado como falho.')

    except Exception as exc:
        logger.exception(f'Erro ao processar notificação MP payment_id={mp_payment_id}: {exc}')
        raise self.retry(exc=exc)


@shared_task
def send_enrollment_confirmation_email(order_id):
    """Envia e-mail de confirmação de matrícula para o aluno."""
    from apps.orders.models import Order
    from django.core.mail import send_mail
    from django.conf import settings

    try:
        order = Order.objects.get(id=order_id)
        courses = [item.course_title for item in order.items.all()]
        subject = f'Matrícula confirmada — FG Cursos'
        message = (
            f'Olá, {order.customer_name}!\n\n'
            f'Sua matrícula foi confirmada nos seguintes cursos:\n'
            + '\n'.join(f'• {c}' for c in courses) +
            f'\n\nAcesse sua área do aluno em: {settings.SITE_URL}/minha-area/\n\n'
            f'FG Centro Educacional\n{settings.SITE_PHONE}\n{settings.SITE_EMAIL}'
        )
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.customer_email],
            fail_silently=True,
        )
    except Exception as exc:
        logger.exception(f'Erro ao enviar e-mail para pedido {order_id}: {exc}')
