from functools import wraps

from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect


CLIENT_GROUP_NAMES = {'client', 'clients', 'клиент', 'клиенты'}
MANAGER_GROUP_NAMES = {'manager', 'managers', 'менеджер', 'менеджеры'}

ROLE_LABELS = {
    'guest': 'Гость',
    'client': 'Клиент',
    'manager': 'Менеджер',
    'admin': 'Администратор',
}


def _normalized_group_names(user):
    if not getattr(user, 'is_authenticated', False):
        return set()
    return {name.strip().lower() for name in user.groups.values_list('name', flat=True)}


def get_user_role(user):
    if not getattr(user, 'is_authenticated', False):
        return 'guest'
    if user.is_superuser:
        return 'admin'

    group_names = _normalized_group_names(user)
    if group_names & MANAGER_GROUP_NAMES:
        return 'manager'
    if group_names & CLIENT_GROUP_NAMES:
        return 'client'
    return 'guest'


def get_role_label(role):
    return ROLE_LABELS.get(role, ROLE_LABELS['guest'])


def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path())

            if get_user_role(request.user) not in allowed_roles:
                messages.error(request, 'У вас нет прав для выполнения этого действия.')
                return redirect('products:product_list')

            return view_func(request, *args, **kwargs)

        return wrapped_view

    return decorator
