from django.shortcuts import render, get_object_or_404
from .models import Course, Category


def catalog_view(request):
    courses = Course.objects.filter(is_active=True).select_related('category')

    category_slug = request.GET.get('categoria')
    level = request.GET.get('nivel')
    modality = request.GET.get('modalidade')

    if category_slug:
        courses = courses.filter(category__slug=category_slug)
    if level:
        courses = courses.filter(level=level)
    if modality:
        courses = courses.filter(modality=modality)

    categories = Category.objects.all()

    context = {
        'courses': courses,
        'categories': categories,
        'level_choices': Course.LEVEL_CHOICES,
        'modality_choices': Course.MODALITY_CHOICES,
        'active_category': category_slug,
        'active_level': level,
        'active_modality': modality,
    }
    return render(request, 'courses/catalog.html', context)


def detail_view(request, slug):
    course = get_object_or_404(Course, slug=slug, is_active=True)
    modules = course.modules.filter(is_active=True).prefetch_related('lessons')

    # Verifica se o usuário já está matriculado
    is_enrolled = False
    enrollment = None
    if request.user.is_authenticated:
        enrollment = course.enrollments.filter(
            student=request.user, status='active'
        ).first()
        is_enrolled = enrollment is not None

    # Verifica se o curso está no carrinho
    cart = request.session.get('cart', {})
    in_cart = str(course.id) in cart

    context = {
        'course': course,
        'modules': modules,
        'is_enrolled': is_enrolled,
        'enrollment': enrollment,
        'in_cart': in_cart,
    }
    return render(request, 'courses/detail.html', context)
