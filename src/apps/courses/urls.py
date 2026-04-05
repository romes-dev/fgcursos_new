from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.catalog_view, name='catalog'),
    path('<slug:slug>/', views.detail_view, name='detail'),
]
