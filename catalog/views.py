from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, LoginForm, DesignRequestForm, CategoryForm, ChangeStatusForm
from .models import User, DesignRequest, Category
from .decorators import admin_required


# главная
def index(request):
    in_progress_count = DesignRequest.objects.filter(status=DesignRequest.STATUS_IN_PROGRESS).count()
    recent_done = DesignRequest.objects.filter(status=DesignRequest.STATUS_DONE).order_by('-created_at')[:4]
    return render(request, 'index.html', {'in_progress_count': in_progress_count, 'recent_done': recent_done})


# регистрация и авторизация
def register_view(request):
    if request.user.is_authenticated: return redirect('index')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Регистрация прошла успешно! Теперь вы можете войти.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated: return redirect('index')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_admin(): return redirect('superadmin_panel')
                return redirect('dashboard')
            else:
                messages.error(request, 'Неверный логин или пароль.')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('index')


# кабинет пользователь
@login_required
def dashboard_view(request):
    user_requests = request.user.requests.all()
    status_filter = request.GET.get('status')
    if status_filter:
        user_requests = user_requests.filter(status=status_filter)
    return render(request, 'dashboard.html', {
        'requests': user_requests,
        'current_status': status_filter,
        'status_choices': DesignRequest.STATUS_CHOICES
    })


@login_required
def create_request_view(request):
    if request.method == 'POST':
        form = DesignRequestForm(request.POST, request.FILES)
        if form.is_valid():
            design_request = form.save(commit=False)
            design_request.user = request.user
            design_request.status = DesignRequest.STATUS_NEW
            design_request.save()
            messages.success(request, 'Заявка успешно создана!')
            return redirect('dashboard')
    else:
        form = DesignRequestForm()
    return render(request, 'create_request.html', {'form': form})


@login_required
def delete_request_view(request, pk):
    design_request = get_object_or_404(DesignRequest, pk=pk)
    if design_request.user != request.user:
        messages.error(request, 'Вы не можете удалить чужую заявку.')
        return redirect('dashboard')
    if design_request.status != DesignRequest.STATUS_NEW:
        messages.error(request, 'Нельзя удалить заявку, которая уже взята в работу.')
        return redirect('dashboard')
    design_request.delete()
    messages.success(request, 'Заявка удалена.')
    return redirect('dashboard')


# админ панель
@admin_required
def superadmin_panel(request):
    all_requests = DesignRequest.objects.all()
    return render(request, 'superadmin/panel.html', {'requests': all_requests})


@admin_required
def change_status(request, pk):
    design_request = get_object_or_404(DesignRequest, pk=pk)
    if design_request.status != DesignRequest.STATUS_NEW:
        messages.error(request, 'Смена статуса для этой заявки невозможна.')
        return redirect('superadmin_panel')

    if request.method == 'POST':
        new_status = request.POST.get('new_status')
        form = ChangeStatusForm(request.POST, request.FILES)

        if new_status == DesignRequest.STATUS_IN_PROGRESS:
            if not request.POST.get('comment'):
                messages.error(request, 'Для перевода в работу необходим комментарий.')
            else:
                design_request.status = DesignRequest.STATUS_IN_PROGRESS
                design_request.comment = request.POST.get('comment')
                design_request.save()
                messages.success(request, 'Заявка принята в работу!')
                return redirect('superadmin_panel')

        elif new_status == DesignRequest.STATUS_DONE:
            if 'design_image' not in request.FILES:
                messages.error(request, 'Для завершения работы необходимо прикрепить изображение дизайна.')
            elif form.is_valid():
                design_request.status = DesignRequest.STATUS_DONE
                design_request.design_image = form.cleaned_data['design_image']
                design_request.save()
                messages.success(request, 'Заявка выполнена!')
                return redirect('superadmin_panel')
    else:
        form = ChangeStatusForm()

    return render(request, 'superadmin/change_status.html', {'req': design_request, 'form': form})


@admin_required
def manage_categories(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Категория добавлена.')
            return redirect('manage_categories')
    else:
        form = CategoryForm()
    return render(request, 'superadmin/categories.html', {'categories': categories, 'form': form})


@admin_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, 'Категория и все её заявки удалены.')
    return redirect('manage_categories')