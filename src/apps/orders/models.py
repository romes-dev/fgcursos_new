import uuid
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User


def generate_order_number():
    return f'FG{str(uuid.uuid4().int)[:10].upper()}'


class Order(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PAID = 'paid'
    STATUS_FAILED = 'failed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_REFUNDED = 'refunded'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Aguardando pagamento'),
        (STATUS_PAID, 'Pago'),
        (STATUS_FAILED, 'Falhou'),
        (STATUS_CANCELLED, 'Cancelado'),
        (STATUS_REFUNDED, 'Reembolsado'),
    ]

    PAYMENT_METHOD_CREDIT_CARD = 'credit_card'
    PAYMENT_METHOD_PIX = 'pix'
    PAYMENT_METHOD_BOLETO = 'boleto'
    PAYMENT_METHOD_CHOICES = [
        (PAYMENT_METHOD_CREDIT_CARD, 'Cartão de crédito'),
        (PAYMENT_METHOD_PIX, 'PIX'),
        (PAYMENT_METHOD_BOLETO, 'Boleto'),
    ]

    number = models.CharField('Número', max_length=20, unique=True, default=generate_order_number)
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='orders', verbose_name='Usuário'
    )
    # Snapshot dos dados do cliente no momento do pedido
    customer_name = models.CharField('Nome do cliente', max_length=200)
    customer_email = models.EmailField('E-mail')
    customer_phone = models.CharField('Telefone', max_length=20, blank=True)
    customer_cpf = models.CharField('CPF', max_length=14, blank=True)

    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    payment_method = models.CharField(
        'Método de pagamento', max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True
    )

    subtotal = models.DecimalField('Subtotal', max_digits=10, decimal_places=2)
    discount = models.DecimalField('Desconto', max_digits=8, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField('Total', max_digits=10, decimal_places=2)

    notes = models.TextField('Observações', blank=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-created_at']

    def __str__(self):
        return f'Pedido #{self.number} — {self.customer_name}'

    def confirm(self):
        """Confirma o pedido, criando matrículas para cada item."""
        from apps.courses.models import Enrollment
        from django.utils import timezone
        from datetime import timedelta

        if self.status == self.STATUS_PAID:
            return  # Já confirmado

        self.status = self.STATUS_PAID
        self.save(update_fields=['status', 'updated_at'])

        for item in self.items.select_related('course'):
            if item.course:
                expires_at = timezone.now() + timedelta(days=item.course.duration_months * 30)
                Enrollment.objects.get_or_create(
                    student=self.user,
                    course=item.course,
                    defaults={
                        'order': self,
                        'status': 'active',
                        'expires_at': expires_at,
                    }
                )


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    course = models.ForeignKey(
        'courses.Course', on_delete=models.SET_NULL, null=True, verbose_name='Curso'
    )
    course_title = models.CharField('Título do curso (snapshot)', max_length=250)
    unit_price = models.DecimalField('Preço unitário', max_digits=10, decimal_places=2)
    total_price = models.DecimalField('Preço total', max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Item do pedido'
        verbose_name_plural = 'Itens do pedido'

    def __str__(self):
        return f'{self.course_title} (Pedido #{self.order.number})'
