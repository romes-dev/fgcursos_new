from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order


@receiver(post_save, sender=Order)
def order_status_changed(sender, instance, created, **kwargs):
    """Quando o admin muda o status para 'paid' manualmente, confirma o pedido."""
    if not created and instance.status == Order.STATUS_PAID:
        # Evita recursão verificando se há matrículas já criadas
        from apps.courses.models import Enrollment
        existing = Enrollment.objects.filter(order=instance).count()
        if existing == 0 and instance.user:
            instance.confirm()
