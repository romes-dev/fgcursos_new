"""
Geração de certificado PDF usando WeasyPrint.
O template HTML é renderizado pelo Django e convertido para PDF.
"""
import io
import logging
from django.template.loader import render_to_string
from django.utils import timezone
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)


def generate_certificate_pdf(enrollment):
    """Gera o PDF do certificado e salva no model Enrollment."""
    try:
        from weasyprint import HTML, CSS
    except ImportError:
        logger.warning('WeasyPrint não instalado. Certificado não gerado.')
        return

    html_string = render_to_string('dashboard/certificate_pdf.html', {
        'enrollment': enrollment,
        'student': enrollment.student,
        'course': enrollment.course,
        'issued_at': timezone.now(),
    })

    pdf_file = io.BytesIO()
    HTML(string=html_string).write_pdf(pdf_file)
    pdf_file.seek(0)

    filename = f'certificado-{enrollment.student.id}-{enrollment.course.slug}.pdf'
    enrollment.certificate_file.save(filename, ContentFile(pdf_file.read()), save=False)
    enrollment.certificate_issued_at = timezone.now()
    enrollment.save(update_fields=['certificate_file', 'certificate_issued_at'])
    logger.info(f'Certificado {filename} gerado e salvo.')
