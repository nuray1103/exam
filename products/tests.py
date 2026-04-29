from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from orders.models import Order

from .models import Category, Manufacturer, Product, Supplier, Unit


def make_product(name='Django для начинающих', quantity=5):
    category, _ = Category.objects.get_or_create(name='Веб-разработка')
    manufacturer, _ = Manufacturer.objects.get_or_create(name='Хабр')
    supplier, _ = Supplier.objects.get_or_create(name='Оптовик книг')
    unit, _ = Unit.objects.get_or_create(name='Штука', abbreviation='шт')
    return Product.objects.create(
        name=name,
        category=category,
        description='Практическая книга',
        manufacturer=manufacturer,
        supplier=supplier,
        price='1200.00',
        unit=unit,
        quantity=quantity,
        discount='0.00',
    )


class ProductPermissionsTests(TestCase):
    def setUp(self):
        Group.objects.get_or_create(name='Клиенты')
        self.admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'pass12345')
        self.client_user = User.objects.create_user('client', password='pass12345')
        self.product = make_product()

    def test_non_admin_cannot_open_product_create(self):
        self.client.force_login(self.client_user)

        response = self.client.get(reverse('products:product_create'))

        self.assertRedirects(response, reverse('products:product_list'))

    def test_product_with_orders_cannot_be_deleted(self):
        Order.objects.create(
            customer=self.client_user,
            product=self.product,
            quantity=1,
            delivery_address='Екатеринбург, Ленина, 10',
        )
        self.client.force_login(self.admin_user)

        response = self.client.post(reverse('products:product_delete', args=[self.product.pk]))

        self.assertRedirects(response, reverse('products:product_list'))
        self.product.refresh_from_db()
