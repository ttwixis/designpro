import re
from django import forms
from django.core.exceptions import ValidationError
from .models import User, DesignRequest, Category


class RegisterForm(forms.ModelForm):
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password_repeat = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    consent = forms.BooleanField(
        label='Согласие на обработку персональных данных',
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        error_messages={'required': 'Необходимо согласие на обработку данных'}
    )

    class Meta:
        model = User
        fields = ['fio', 'username', 'email']
        labels = {'fio': 'ФИО', 'username': 'Логин', 'email': 'Email'}
        help_texts = {'username': ''}
        widgets = {
            'fio': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Подсвечиваем на стороне сервера каждое поле, для которого найдена ошибка.
        for field_name in self.errors:
            if field_name in self.fields:
                css_class = self.fields[field_name].widget.attrs.get('class', '')
                self.fields[field_name].widget.attrs['class'] = f'{css_class} is-invalid'.strip()

    def clean_fio(self):
        fio = self.cleaned_data.get('fio')
        if not re.fullmatch(r'[А-Яа-яЁё\s-]+', fio or ''):
            raise ValidationError('ФИО может содержать только кириллические буквы, пробелы и дефис.')
        return fio

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not re.fullmatch(r'[a-zA-Z-]+', username or ''):
            raise ValidationError('Логин может содержать только латиницу и дефис.')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Пользователь с таким логином уже существует.')
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_repeat = cleaned_data.get('password_repeat')
        if password and password_repeat and password != password_repeat:
            self.add_error('password_repeat', 'Пароли не совпадают.')
        return cleaned_data


class LoginForm(forms.Form):
    username = forms.CharField(
        label='Логин',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите логин'})
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Введите пароль'})
    )


class DesignRequestForm(forms.ModelForm):
    class Meta:
        model = DesignRequest
        fields = ['title', 'description', 'category', 'image']
        labels = {
            'title': 'Название заявки',
            'description': 'Описание',
            'category': 'Категория',
            'image': 'Фото помещения (до 2 МБ)'
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 2 * 1024 * 1024:
                raise ValidationError('Максимальный размер файла — 2 МБ.')
            ext = image.name.rsplit('.', 1)[-1].lower() if '.' in image.name else ''
            if ext not in ['jpg', 'jpeg', 'png', 'bmp']:
                raise ValidationError('Допустимые форматы: jpg, jpeg, png, bmp.')
        return image


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название категории'})}


class ChangeStatusForm(forms.Form):
    comment = forms.CharField(
        label='Комментарий',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2})
    )
    design_image = forms.ImageField(
        label='Изображение дизайна',
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
