from django.conf import settings


def site_settings(request):
    return {
        'SITE_NAME': settings.SITE_NAME,
        'SITE_URL': settings.SITE_URL,
        'SITE_PHONE': settings.SITE_PHONE,
        'SITE_WHATSAPP': settings.SITE_WHATSAPP,
        'SITE_EMAIL': settings.SITE_EMAIL,
        'SITE_ADDRESS': settings.SITE_ADDRESS,
        'SITE_INSTAGRAM': settings.SITE_INSTAGRAM,
    }
