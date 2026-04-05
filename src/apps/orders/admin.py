from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('course', 'course_title', 'unit_price', 'total_price')
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('number', 'customer_name', 'customer_email', 'status_badge', 'total', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('number', 'customer_name', 'customer_email', 'customer_cpf')
    readonly_fields = ('number', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    actions = ['confirm_orders', 'cancel_orders']
    fieldsets = (
        ('Identificação', {'fields': ('number', 'user', 'status', 'payment_method')}),
        ('Cliente', {'fields': ('customer_name', 'customer_email', 'customer_phone', 'customer_cpf')}),
        ('Valores', {'fields': ('subtotal', 'discount', 'total')}),
        ('Informações', {'fields': ('notes', 'created_at', 'updated_at')}),
    )

    def status_badge(self, obj):
        colors = {
            'pending': '#f59e0b',
            'paid': '#10b981',
            'failed': '#ef4444',
            'cancelled': '#6b7280',
            'refunded': '#8b5cf6',
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;border-radius:4px;font-size:12px">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def confirm_orders(self, request, queryset):
        confirmed = 0
        for order in queryset.filter(status=Order.STATUS_PENDING):
            if order.user:
                order.confirm()
                confirmed += 1
        self.message_user(request, f'{confirmed} pedido(s) confirmado(s) e matrículas criadas.')
    confirm_orders.short_description = 'Confirmar pagamento e criar matrículas'

    def cancel_orders(self, request, queryset):
        updated = queryset.exclude(status=Order.STATUS_PAID).update(status=Order.STATUS_CANCELLED)
        self.message_user(request, f'{updated} pedido(s) cancelado(s).')
    cancel_orders.short_description = 'Cancelar pedidos selecionados'
