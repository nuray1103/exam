from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from accounts.roles import get_user_role, role_required
from .models import Product, Supplier
from .forms import ProductForm

# /products?search="test user"
def product_list(request):
    """Список книг в каталоге с учётом роли пользователя"""
    user_role = get_user_role(request.user) if request.user.is_authenticated else 'guest'

    # Базовый queryset
    products = Product.objects.select_related('category', 'manufacturer', 'supplier', 'unit')

    # Фильтры и поиск доступны только администратору
    if user_role == 'admin':
        # Поиск
        search_query = request.GET.get('search', '')
        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(category__name__icontains=search_query) |
                Q(manufacturer__name__icontains=search_query) |
                Q(supplier__name__icontains=search_query) |
                Q(unit__name__icontains=search_query)
            )

        # Фильтр по поставщику
        supplier_filter = request.GET.get('supplier', '')
        if supplier_filter:
            products = products.filter(supplier__id=supplier_filter)

        # Сортировка
        sort_by = request.GET.get('sort', 'name')
        sort_map = {
            'name': 'name',
            'quantity_asc': 'quantity',
            'quantity_desc': '-quantity',
        }
        products = products.order_by(sort_map.get(sort_by, 'name'))

        suppliers = Supplier.objects.all()
    else:
        suppliers = None
        search_query = ''
        supplier_filter = ''
        sort_by = 'name'

    if user_role != 'admin':
        products = products.order_by('name')

    # Пагинация
    paginator = Paginator(products, 10)  # 10 позиций на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'user_role': user_role,
        'suppliers': suppliers,
        'search_query': search_query,
        'supplier_filter': supplier_filter,
        'sort_by': sort_by,
    }

    return render(request, 'products/product_list.html', context)


@role_required('admin')
def product_create(request):
    """Добавление новой книги (только для администраторов)"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Книга успешно добавлена в каталог.')
            return redirect('products:product_list')
    else:
        form = ProductForm()

    return render(request, 'products/product_form.html', {
        'form': form,
        'title': 'Добавить книгу',
        'user_role': get_user_role(request.user),
    })


@role_required('admin')
def product_update(request, pk):
    """Редактирование карточки книги (только для администраторов)"""
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            if 'image' in request.FILES and product.image:
                product.image.delete(save=False)
            form.save()
            messages.success(request, 'Книга успешно обновлена.')
            return redirect('products:product_list')
    else:
        form = ProductForm(instance=product)

    return render(request, 'products/product_form.html', {
        'form': form,
        'product': product,
        'title': 'Редактировать книгу',
        'user_role': get_user_role(request.user),
    })


@role_required('admin')
def product_delete(request, pk):
    """Удаление книги из каталога (только для администраторов)"""
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        if product.orders.exists():
            messages.error(
                request,
                'Нельзя удалить книгу, пока по ней существуют оформленные заказы.',
            )
            return redirect('products:product_list')

        # Удаляем изображение
        if product.image:
            product.image.delete()
        product.delete()
        messages.success(request, 'Книга успешно удалена из каталога.')
        return redirect('products:product_list')

    return render(request, 'products/product_confirm_delete.html', {
        'product': product,
        'user_role': get_user_role(request.user)
    })
