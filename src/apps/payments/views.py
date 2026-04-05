import hashlib
import hmac
import json
import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.orders.models import Order
from .gateways.mercadopago import MercadoPagoGateway
from .models import Payment
from .tasks import process_payment_notification

logger = logging.getLogger(__name__)


@login_required
def create_payment_view(request, order_number):
    """Cria preferência no Mercado Pago e redireciona o aluno."""
    order = get_object_or_404(Order, number=order_number, user=request.user)

    if order.status != Order.STATUS_PENDING:
        return redirect('orders:detail', number=order.number)

    gateway = MercadoPagoGateway()
    preference = gateway.create_preference(order)

    Payment.objects.update_or_create(
        order=order,
        gateway=Payment.GATEWAY_MERCADOPAGO,
        defaults={
            'gateway_preference_id': preference['preference_id'],
            'status': Payment.STATUS_PENDING,
            'amount': order.total,
        }
    )

    # Em sandbox, use sandbox_init_point; em produção, use init_point
    if settings.DEBUG:
        redirect_url = preference.get('sandbox_init_point') or preference.get('init_point')
    else:
        redirect_url = preference.get('init_point')

    return redirect(redirect_url)


@login_required
def payment_success_view(request):
    payment_id = request.GET.get('payment_id')
    order_number = request.GET.get('external_reference') or request.GET.get('preference_id', '')

    if payment_id:
        process_payment_notification.delay(payment_id)

    order = None
    if order_number and order_number.startswith('FG'):
        order = Order.objects.filter(number=order_number, user=request.user).first()

    return render(request, 'orders/payment_success.html', {'order': order})


@login_required
def payment_pending_view(request):
    return render(request, 'orders/payment_pending.html')


@login_required
def payment_failure_view(request):
    return render(request, 'orders/payment_failure.html')


@csrf_exempt
@require_POST
def mercadopago_webhook(request):
    """
    Recebe notificações IPN do Mercado Pago.
    Valida assinatura HMAC e enfileira tarefa Celery.
    """
    # Validação da assinatura (x-signature header)
    signature = request.headers.get('x-signature', '')
    request_id = request.headers.get('x-request-id', '')

    if settings.MP_WEBHOOK_SECRET and signature:
        # Formato: ts=<timestamp>,v1=<hash>
        parts = dict(part.split('=', 1) for part in signature.split(',') if '=' in part)
        ts = parts.get('ts', '')
        v1 = parts.get('v1', '')

        # Monta a string a ser verificada
        query_string = request.META.get('QUERY_STRING', '')
        data_id = request.GET.get('data.id', '')
        manifest = f'id:{data_id};request-id:{request_id};ts:{ts};'

        expected = hmac.new(
            settings.MP_WEBHOOK_SECRET.encode(),
            manifest.encode(),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(expected, v1):
            logger.warning('Webhook MP: assinatura inválida.')
            return HttpResponseBadRequest('Invalid signature')

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponseBadRequest('Invalid JSON')

    event_type = body.get('type') or request.GET.get('type')
    data_id = body.get('data', {}).get('id') or request.GET.get('data.id')

    if event_type == 'payment' and data_id:
        logger.info(f'Webhook MP: payment_id={data_id}')
        process_payment_notification.delay(data_id)

    return HttpResponse(status=200)
