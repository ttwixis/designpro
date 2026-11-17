from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """ модель пользователя с ФИО и ролью."""
    ROLE_USER = 'user'
    ROLE_ADMIN = 'admin'
    ROLE_CHOICES = [
        (ROLE_USER, 'Пользователь'),
        (ROLE_ADMIN, 'Администратор'),
    ]

    fio = models.CharField('ФИО', max_length=150)
    role = models.CharField('Роль', max_length=10, choices=ROLE_CHOICES, default=ROLE_USER)
    email = models.EmailField('Email', unique=True)

    def is_admin(self):
        return self.role == self.ROLE_ADMIN


class Category(models.Model):
    """Категории заявок """
    name = models.CharField('Название', max_length=100, unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name


class DesignRequest(models.Model):
    """Заявка на дизайн интерьера."""
    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_DONE = 'done'
    STATUS_CHOICES = [
        (STATUS_NEW, 'Новая'),
        (STATUS_IN_PROGRESS, 'Принято в работу'),
        (STATUS_DONE, 'Выполнено'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests', verbose_name='Пользователь')
    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание')
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='requests', verbose_name='Категория'
    )
    image = models.ImageField('Фото/план помещения', upload_to='requests/')
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    # Поля для администратора
    comment = models.TextField('Комментарий администратора', blank=True)
    design_image = models.ImageField('Изображение дизайна', upload_to='designs/', blank=True, null=True)

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_at']  # Сначала новые

    def __str__(self):
        return f'{self.title} ({self.get_status_display()})'