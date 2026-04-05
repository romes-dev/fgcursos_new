from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('criar/<str:order_number>/', views.create_payment_view, name='create'),
    path('sucesso/', views.payment_success_view, name='success'),
    path('pendente/', views.payment_pending_view, name='pending'),
    path('falha/', views.payment_failure_view, name='failure'),
    path('webhook/mercadopago/', views.mercadopago_webhook, name='mp_webhook'),
]
