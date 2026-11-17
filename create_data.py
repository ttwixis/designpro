import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'designpro.settings')
django.setup()

from catalog.models import User, Category

User.objects.create_superuser(
    username='admin',
    email='admin@example.com',
    password='admin',
    fio='Главный Администратор',
    role='admin',
)

Category.objects.bulk_create([
    Category(name='3D-дизайн'),
    Category(name='2D-дизайн'),
    Category(name='Эскиз'),
])

print("Админ и категории успешно созданы!")