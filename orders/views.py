from django.core.paginator import Paginator
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from accounts.roles import get_user_role, role_required

from .forms import OrderForm
from .models import Order


def _get_visible_orders(user):
    role = get_user_role(user)
    orders = Order.objects.select_related('customer', 'product')

    if role == 'client':
        orders = orders.filter(customer=user)

    return orders


def _get_user_order_or_404(user, pk):
    return get_object_or_404(_get_visible_orders(user), pk=pk)


@role_required('client', 'manager', 'admin')
def order_list(request):
    user_role = get_user_role(request.user)
    orders = _get_visible_orders(request.user)

    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'orders/order_list.html', {
        'page_obj': page_obj,
        'user_role': user_role,
    })


@role_required('client', 'manager', 'admin')
def order_create(request):
    user_role = get_user_role(request.user)

    if request.method == 'POST':
        form = OrderForm(request.POST, user_role=user_role)
        if form.is_valid():
            order = form.save(commit=False)
            if user_role == 'client':
                order.customer = request.user
            order.save()
            messages.success(request, 'Заказ успешно создан.')
            return redirect('orders:order_list')
    else:
        form = OrderForm(user_role=user_role)

    return render(request, 'orders/order_form.html', {
        'form': form,
        'title': 'Оформить заказ',
        'submit_label': 'Создать заказ',
        'user_role': user_role,
    })


@role_required('client', 'manager', 'admin')
def order_update(request, pk):
    user_role = get_user_role(request.user)
    order = _get_user_order_or_404(request.user, pk)

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order, user_role=user_role)
        if form.is_valid():
            updated_order = form.save(commit=False)
            if user_role == 'client':
                updated_order.customer = request.user
            updated_order.save()
            messages.success(request, 'Заказ успешно обновлён.')
            return redirect('orders:order_list')
    else:
        form = OrderForm(instance=order, user_role=user_role)

    return render(request, 'orders/order_form.html', {
        'form': form,
        'order': order,
        'title': f'Редактировать заказ #{order.pk}',
        'submit_label': 'Сохранить изменения',
        'user_role': user_role,
    })


@role_required('client', 'manager', 'admin')
def order_delete(request, pk):
    user_role = get_user_role(request.user)
    order = _get_user_order_or_404(request.user, pk)

    if request.method == 'POST':
        order.delete()
        messages.success(request, 'Заказ успешно удалён.')
        return redirect('orders:order_list')

    return render(request, 'orders/order_confirm_delete.html', {
        'order': order,
        'user_role': user_role,
    })
