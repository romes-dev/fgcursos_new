from django.db import models


class Payment(models.Model):
    GATEWAY_MERCADOPAGO = 'mercadopago'
    GATEWAY_MANUAL = 'manual'
    GATEWAY_CHOICES = [
        (GATEWAY_MERCADOPAGO, 'Mercado Pago'),
        (GATEWAY_MANUAL, 'Manual (admin)'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_IN_PROCESS = 'in_process'
    STATUS_REFUNDED = 'refunded'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pendente'),
        (STATUS_APPROVED, 'Aprovado'),
        (STATUS_REJECTED, 'Rejeitado'),
        (STATUS_IN_PROCESS, 'Em processo'),
        (STATUS_REFUNDED, 'Reembolsado'),
        (STATUS_CANCELLED, 'Cancelado'),
    ]

    order = models.ForeignKey(
        'orders.Order', on_delete=models.CASCADE,
        related_name='payments', verbose_name='Pedido'
    )
    gateway = models.CharField('Gateway', max_length=20, choices=GATEWAY_CHOICES)
    gateway_payment_id = models.CharField('ID externo (gateway)', max_length=200, blank=True)
    gateway_preference_id = models.CharField('ID da preferência (MP)', max_length=200, blank=True)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    amount = models.DecimalField('Valor', max_digits=10, decimal_places=2)
    payment_method = models.CharField('Método', max_length=50, blank=True)
    raw_response = models.JSONField('Resposta bruta do gateway', default=dict, blank=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Pagamento'
        verbose_name_plural = 'Pagamentos'
        ordering = ['-created_at']

    def __str__(self):
        return f'Pagamento #{self.id} — Pedido {self.order.number} ({self.get_status_display()})'
