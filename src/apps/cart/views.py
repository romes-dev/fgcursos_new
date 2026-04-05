from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from apps.courses.models import Course
from .cart import Cart


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart/cart.html', {'cart': cart})


@require_POST
def cart_add(request, course_id):
    cart = Cart(request)
    course = get_object_or_404(Course, id=course_id, is_active=True)

    # Verifica se o usuário já está matriculado
    if request.user.is_authenticated:
        if course.enrollments.filter(student=request.user, status='active').exists():
            if request.htmx:
                return render(request, 'cart/partials/cart_widget.html', {
                    'cart_count': len(cart),
                    'message': 'Você já está matriculado neste curso.',
                })
            messages.warning(request, 'Você já está matriculado neste curso.')
            return redirect('courses:detail', slug=course.slug)

    cart.add(course)

    if request.htmx:
        return render(request, 'cart/partials/cart_widget.html', {
            'cart_count': len(cart),
            'course_added': course.title,
        })

    messages.success(request, f'"{course.title}" adicionado ao carrinho.')
    return redirect('cart:detail')


@require_POST
def cart_remove(request, course_id):
    cart = Cart(request)
    cart.remove(course_id)

    if request.htmx:
        return render(request, 'cart/partials/cart_items.html', {'cart': cart})

    messages.info(request, 'Curso removido do carrinho.')
    return redirect('cart:detail')
