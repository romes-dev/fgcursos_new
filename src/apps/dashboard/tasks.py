import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def generate_certificate(enrollment_id):
    from apps.courses.models import Enrollment
    from .certificate import generate_certificate_pdf

    try:
        enrollment = Enrollment.objects.select_related('student', 'course').get(pk=enrollment_id)
        if enrollment.completion_percent == 100:
            generate_certificate_pdf(enrollment)
            logger.info(f'Certificado gerado para matrícula {enrollment_id}')
    except Exception as exc:
        logger.exception(f'Erro ao gerar certificado para matrícula {enrollment_id}: {exc}')
