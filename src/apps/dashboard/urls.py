from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('curso/<slug:slug>/', views.my_course_view, name='my_course'),
    path('curso/<slug:course_slug>/aula/<int:lesson_pk>/', views.lesson_view, name='lesson'),
    path('aula/<int:lesson_pk>/completar/', views.mark_lesson_complete, name='complete_lesson'),
    path('certificado/<int:enrollment_id>/', views.download_certificate, name='certificate'),
]
