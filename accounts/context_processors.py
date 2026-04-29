from .roles import get_role_label, get_user_role


def current_user_role(request):
    role = get_user_role(request.user)
    return {
        'current_user_role': role,
        'current_user_role_label': get_role_label(role),
    }
