from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Course, Module, Lesson, Enrollment, LessonProgress


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ('title', 'lesson_type', 'order', 'is_active', 'is_free_preview', 'duration_minutes')


class ModuleInline(admin.StackedInline):
    model = Module
    extra = 1
    show_change_link = True
    fields = ('title', 'description', 'order', 'is_active')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'modality', 'price', 'is_active', 'is_featured', 'enrollment_count')
    list_filter = ('level', 'modality', 'is_active', 'is_featured', 'category')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ModuleInline]
    list_editable = ('is_active', 'is_featured', 'price')
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('title', 'slug', 'category', 'level', 'modality', 'short_description', 'description')
        }),
        ('Mídia', {
            'fields': ('cover_image', 'promo_video_url')
        }),
        ('Precificação', {
            'fields': ('price', 'compare_price')
        }),
        ('Dados Acadêmicos', {
            'fields': ('workload_hours', 'duration_months', 'has_internship', 'internship_hours')
        }),
        ('Publicação', {
            'fields': ('is_active', 'is_featured', 'certificate_template')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
    )

    def enrollment_count(self, obj):
        count = obj.enrollments.filter(status='active').count()
        return format_html('<strong>{}</strong> alunos', count)
    enrollment_count.short_description = 'Matrículas ativas'


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'is_active')
    list_filter = ('course', 'is_active')
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'lesson_type', 'order', 'is_active', 'is_free_preview')
    list_filter = ('lesson_type', 'is_active', 'is_free_preview', 'module__course')
    search_fields = ('title',)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'status', 'enrolled_at', 'expires_at', 'completion_display')
    list_filter = ('status', 'course', 'enrolled_at')
    search_fields = ('student__first_name', 'student__last_name', 'student__email', 'course__title')
    raw_id_fields = ('student', 'course', 'order')
    readonly_fields = ('enrolled_at',)
    actions = ['activate_enrollments', 'cancel_enrollments']

    def completion_display(self, obj):
        pct = obj.completion_percent
        color = 'green' if pct == 100 else 'orange' if pct > 50 else 'gray'
        return format_html(
            '<span style="color:{}">{}%</span>', color, pct
        )
    completion_display.short_description = 'Conclusão'

    def activate_enrollments(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} matrícula(s) ativada(s).')
    activate_enrollments.short_description = 'Ativar matrículas selecionadas'

    def cancel_enrollments(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} matrícula(s) cancelada(s).')
    cancel_enrollments.short_description = 'Cancelar matrículas selecionadas'
