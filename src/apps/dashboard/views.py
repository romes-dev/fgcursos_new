import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.http import require_POST

from apps.courses.models import Enrollment, Lesson, LessonProgress, Course

logger = logging.getLogger(__name__)


@login_required
def dashboard_home(request):
    enrollments = (
        Enrollment.objects
        .filter(student=request.user, status='active')
        .select_related('course')
        .prefetch_related('progress')
        .order_by('-enrolled_at')
    )
    context = {'enrollments': enrollments}
    return render(request, 'dashboard/home.html', context)


@login_required
def my_course_view(request, slug):
    course = get_object_or_404(Course, slug=slug, is_active=True)
    enrollment = get_object_or_404(
        Enrollment, student=request.user, course=course, status='active'
    )
    modules = course.modules.filter(is_active=True).prefetch_related(
        'lessons__lessonprogress_set'
    )

    # Monta mapa de progresso
    completed_ids = set(
        enrollment.progress.filter(completed=True).values_list('lesson_id', flat=True)
    )

    context = {
        'course': course,
        'enrollment': enrollment,
        'modules': modules,
        'completed_ids': completed_ids,
        'completion_percent': enrollment.completion_percent,
    }
    return render(request, 'dashboard/my_course.html', context)


@login_required
def lesson_view(request, course_slug, lesson_pk):
    course = get_object_or_404(Course, slug=course_slug, is_active=True)
    enrollment = get_object_or_404(
        Enrollment, student=request.user, course=course, status='active'
    )
    lesson = get_object_or_404(Lesson, pk=lesson_pk, module__course=course, is_active=True)

    # Obtém ou cria o progresso desta aula
    progress, _ = LessonProgress.objects.get_or_create(
        enrollment=enrollment,
        lesson=lesson
    )

    # Próxima e anterior
    module_lessons = list(
        Lesson.objects.filter(module=lesson.module, is_active=True).order_by('order', 'pk')
    )
    try:
        idx = next(i for i, l in enumerate(module_lessons) if l.pk == lesson.pk)
        prev_lesson = module_lessons[idx - 1] if idx > 0 else None
        next_lesson = module_lessons[idx + 1] if idx < len(module_lessons) - 1 else None
    except StopIteration:
        prev_lesson = next_lesson = None

    context = {
        'course': course,
        'lesson': lesson,
        'enrollment': enrollment,
        'progress': progress,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
        'completion_percent': enrollment.completion_percent,
    }
    return render(request, 'dashboard/lesson.html', context)


@login_required
@require_POST
def mark_lesson_complete(request, lesson_pk):
    lesson = get_object_or_404(Lesson, pk=lesson_pk, is_active=True)
    enrollment = get_object_or_404(
        Enrollment, student=request.user, course=lesson.module.course, status='active'
    )

    progress, _ = LessonProgress.objects.get_or_create(enrollment=enrollment, lesson=lesson)
    if not progress.completed:
        progress.completed = True
        progress.completed_at = timezone.now()
        progress.save()

    # Se concluiu 100%, agenda geração de certificado
    if enrollment.completion_percent == 100 and not enrollment.certificate_file:
        from .tasks import generate_certificate
        generate_certificate.delay(enrollment.id)

    if request.htmx:
        return render(request, 'dashboard/partials/progress_bar.html', {
            'completion_percent': enrollment.completion_percent,
            'enrollment': enrollment,
        })

    return JsonResponse({'completion_percent': enrollment.completion_percent})


@login_required
def download_certificate(request, enrollment_id):
    enrollment = get_object_or_404(
        Enrollment, pk=enrollment_id, student=request.user, status='active'
    )

    if not enrollment.certificate_file:
        if enrollment.completion_percent < 100:
            raise Http404('Certificado disponível apenas após concluir 100% do curso.')
        # Gera agora se ainda não foi gerado
        from .certificate import generate_certificate_pdf
        generate_certificate_pdf(enrollment)
        enrollment.refresh_from_db()

    response = HttpResponse(
        enrollment.certificate_file.read(),
        content_type='application/pdf'
    )
    response['Content-Disposition'] = (
        f'attachment; filename="certificado-{enrollment.course.slug}.pdf"'
    )
    return response
