from django.shortcuts import render
from apps.courses.models import Course, Category


def home_view(request):
    featured_courses = Course.objects.filter(is_active=True, is_featured=True).select_related('category')[:6]
    all_courses = Course.objects.filter(is_active=True).select_related('category')
    categories = Category.objects.all()

    context = {
        'featured_courses': featured_courses,
        'all_courses': all_courses,
        'categories': categories,
    }
    return render(request, 'core/home.html', context)


def about_view(request):
    return render(request, 'core/about.html')
