from django.contrib import admin
from django.utils.html import format_html
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_link', 'gateway', 'status_badge', 'amount', 'payment_method', 'created_at')
    list_filter = ('gateway', 'status', 'created_at')
    search_fields = ('order__number', 'gateway_payment_id', 'gateway_preference_id')
    readonly_fields = ('created_at', 'updated_at', 'raw_response')

    def order_link(self, obj):
        return format_html('<a href="/admin/orders/order/{}/change/">{}</a>', obj.order.id, obj.order.number)
    order_link.short_description = 'Pedido'

    def status_badge(self, obj):
        colors = {
            'pending': '#f59e0b',
            'approved': '#10b981',
            'rejected': '#ef4444',
            'in_process': '#3b82f6',
            'refunded': '#8b5cf6',
            'cancelled': '#6b7280',
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;border-radius:4px;font-size:12px">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
