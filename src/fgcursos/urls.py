from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = 'FG Cursos — Administração'
admin.site.site_title = 'FG Cursos'
admin.site.index_title = 'Painel Administrativo'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('conta/', include('apps.accounts.urls')),
    path('', include('apps.core.urls')),
    path('cursos/', include('apps.courses.urls')),
    path('carrinho/', include('apps.cart.urls')),
    path('pedidos/', include('apps.orders.urls')),
    path('pagamentos/', include('apps.payments.urls')),
    path('minha-area/', include('apps.dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
