from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name='detail'),
    path('adicionar/<int:course_id>/', views.cart_add, name='add'),
    path('remover/<int:course_id>/', views.cart_remove, name='remove'),
]
