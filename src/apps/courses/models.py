from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse


class Category(models.Model):
    name = models.CharField('Nome', max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField('Descrição', blank=True)
    icon = models.CharField('Ícone (classe CSS)', max_length=50, blank=True)
    order = models.PositiveIntegerField('Ordem', default=0)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Course(models.Model):
    LEVEL_EJA_FUNDAMENTAL = 'eja_fund'
    LEVEL_EJA_MEDIO = 'eja_medio'
    LEVEL_TECNICO = 'tecnico'
    LEVEL_CHOICES = [
        (LEVEL_EJA_FUNDAMENTAL, 'EJA Fundamental II'),
        (LEVEL_EJA_MEDIO, 'EJA Ensino Médio'),
        (LEVEL_TECNICO, 'Técnico'),
    ]

    MODALITY_PRESENCIAL = 'presencial'
    MODALITY_EAD = 'ead'
    MODALITY_HIBRIDO = 'hibrido'
    MODALITY_CHOICES = [
        (MODALITY_PRESENCIAL, 'Presencial'),
        (MODALITY_EAD, 'EAD'),
        (MODALITY_HIBRIDO, 'Híbrido (EAD + Presencial)'),
    ]

    title = models.CharField('Título', max_length=250)
    slug = models.SlugField(unique=True, max_length=250)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='courses', verbose_name='Categoria'
    )
    level = models.CharField('Nível', max_length=20, choices=LEVEL_CHOICES)
    modality = models.CharField('Modalidade', max_length=20, choices=MODALITY_CHOICES, default=MODALITY_EAD)
    description = models.TextField('Descrição completa')
    short_description = models.CharField('Descrição curta', max_length=500, blank=True)
    cover_image = models.ImageField('Imagem de capa', upload_to='courses/covers/', blank=True, null=True)
    promo_video_url = models.URLField('URL do vídeo promocional', blank=True)
    price = models.DecimalField('Preço (à vista)', max_digits=10, decimal_places=2)
    compare_price = models.DecimalField(
        'Preço original (riscado)', max_digits=10, decimal_places=2,
        null=True, blank=True, help_text='Preço antes do desconto'
    )
    workload_hours = models.PositiveIntegerField('Carga horária (horas)')
    duration_months = models.PositiveIntegerField('Duração (meses)', default=6)
    is_active = models.BooleanField('Ativo', default=True)
    is_featured = models.BooleanField('Destaque na home', default=False)
    has_internship = models.BooleanField('Possui estágio', default=False)
    internship_hours = models.PositiveIntegerField('Horas de estágio', default=0)
    certificate_template = models.FileField(
        'Template do certificado', upload_to='courses/certificates/',
        blank=True, null=True
    )
    meta_title = models.CharField('Meta title (SEO)', max_length=250, blank=True)
    meta_description = models.CharField('Meta description (SEO)', max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        ordering = ['title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('courses:detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def has_discount(self):
        return self.compare_price and self.compare_price > self.price

    @property
    def discount_percent(self):
        if self.has_discount:
            return int((1 - self.price / self.compare_price) * 100)
        return 0

    @property
    def total_workload(self):
        return self.workload_hours + self.internship_hours


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField('Título', max_length=250)
    description = models.TextField('Descrição', blank=True)
    order = models.PositiveIntegerField('Ordem', default=0)
    is_active = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Módulo'
        verbose_name_plural = 'Módulos'
        ordering = ['order', 'title']

    def __str__(self):
        return f'{self.course.title} — {self.title}'


class Lesson(models.Model):
    TYPE_VIDEO = 'video'
    TYPE_PDF = 'pdf'
    TYPE_TEXT = 'text'
    TYPE_CHOICES = [
        (TYPE_VIDEO, 'Vídeo'),
        (TYPE_PDF, 'PDF'),
        (TYPE_TEXT, 'Texto'),
    ]

    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField('Título', max_length=250)
    lesson_type = models.CharField('Tipo', max_length=10, choices=TYPE_CHOICES)
    order = models.PositiveIntegerField('Ordem', default=0)
    is_active = models.BooleanField('Ativo', default=True)
    is_free_preview = models.BooleanField('Aula gratuita (prévia)', default=False)
    duration_minutes = models.PositiveIntegerField('Duração (minutos)', default=0)
    # Conteúdo — apenas um campo preenchido por tipo
    video_url = models.URLField('URL do vídeo (YouTube/Vimeo)', blank=True)
    video_file = models.FileField('Arquivo de vídeo', upload_to='lessons/videos/', blank=True, null=True)
    pdf_file = models.FileField('Arquivo PDF', upload_to='lessons/pdfs/', blank=True, null=True)
    text_content = models.TextField('Conteúdo em texto/HTML', blank=True)

    class Meta:
        verbose_name = 'Aula'
        verbose_name_plural = 'Aulas'
        ordering = ['order', 'title']

    def __str__(self):
        return f'{self.module.title} — {self.title}'


class Enrollment(models.Model):
    STATUS_ACTIVE = 'active'
    STATUS_EXPIRED = 'expired'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Ativa'),
        (STATUS_EXPIRED, 'Expirada'),
        (STATUS_CANCELLED, 'Cancelada'),
    ]

    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='enrollments', verbose_name='Aluno'
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='enrollments', verbose_name='Curso'
    )
    order = models.ForeignKey(
        'orders.Order', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='enrollments', verbose_name='Pedido'
    )
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    enrolled_at = models.DateTimeField('Matriculado em', auto_now_add=True)
    expires_at = models.DateTimeField('Expira em', null=True, blank=True)
    certificate_file = models.FileField(
        'Certificado gerado', upload_to='certificates/', blank=True, null=True
    )
    certificate_issued_at = models.DateTimeField('Certificado emitido em', null=True, blank=True)

    class Meta:
        verbose_name = 'Matrícula'
        verbose_name_plural = 'Matrículas'
        unique_together = ['student', 'course']
        ordering = ['-enrolled_at']

    def __str__(self):
        return f'{self.student.get_full_name()} — {self.course.title}'

    @property
    def completion_percent(self):
        total = Lesson.objects.filter(module__course=self.course, is_active=True).count()
        if not total:
            return 0
        completed = self.progress.filter(completed=True).count()
        return int((completed / total) * 100)

    @property
    def is_completed(self):
        return self.completion_percent == 100


class LessonProgress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField('Concluída', default=False)
    completed_at = models.DateTimeField('Concluída em', null=True, blank=True)
    last_position_seconds = models.PositiveIntegerField('Posição no vídeo (seg)', default=0)

    class Meta:
        verbose_name = 'Progresso de Aula'
        verbose_name_plural = 'Progresso de Aulas'
        unique_together = ['enrollment', 'lesson']

    def __str__(self):
        status = 'Concluída' if self.completed else 'Em andamento'
        return f'{self.enrollment.student.get_full_name()} — {self.lesson.title} ({status})'
