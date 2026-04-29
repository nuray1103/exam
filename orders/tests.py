from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from products.models import Category, Manufacturer, Product, Supplier, Unit

from .models import Order


def make_product(name='Книга по Python', quantity=5):
    category, _ = Category.objects.get_or_create(name='Программирование')
    manufacturer, _ = Manufacturer.objects.get_or_create(name='Питер')
    supplier, _ = Supplier.objects.get_or_create(name='Книжный склад')
    unit, _ = Unit.objects.get_or_create(name='Штука', abbreviation='шт')
    return Product.objects.create(
        name=name,
        category=category,
        description='Учебное пособие',
        manufacturer=manufacturer,
        supplier=supplier,
        price='1000.00',
        unit=unit,
        quantity=quantity,
        discount='10.00',
    )


class OrdersAccessTests(TestCase):
    def setUp(self):
        self.clients_group, _ = Group.objects.get_or_create(name='Клиенты')
        self.managers_group, _ = Group.objects.get_or_create(name='Менеджеры')

        self.client_user = User.objects.create_user('client', password='pass12345')
        self.client_user.groups.add(self.clients_group)

        self.other_client = User.objects.create_user('client2', password='pass12345')
        self.other_client.groups.add(self.clients_group)

        self.manager_user = User.objects.create_user('manager', password='pass12345')
        self.manager_user.groups.add(self.managers_group)

        self.product = make_product()
        self.order = Order.objects.create(
            customer=self.client_user,
            product=self.product,
            quantity=2,
            delivery_address='Москва, ул. Пушкина, д. 1',
        )

    def test_client_sees_only_own_orders(self):
        other_product = make_product(name='Алгоритмы', quantity=4)
        Order.objects.create(
            customer=self.other_client,
            product=other_product,
            quantity=1,
            delivery_address='Санкт-Петербург, Невский, 1',
        )

        self.client.force_login(self.client_user)
        response = self.client.get(reverse('orders:order_list'))

        self.assertContains(response, f'Заказ #{self.order.pk}')
        self.assertNotContains(response, other_product.name)

    def test_client_cannot_edit_foreign_order(self):
        foreign_order = Order.objects.create(
            customer=self.other_client,
            product=self.product,
            quantity=1,
            delivery_address='Санкт-Петербург, Невский, 1',
        )

        self.client.force_login(self.client_user)
        response = self.client.get(reverse('orders:order_update', args=[foreign_order.pk]))

        self.assertEqual(response.status_code, 404)

    def test_manager_can_see_all_orders(self):
        other_product = make_product(name='Чистый код', quantity=7)
        Order.objects.create(
            customer=self.other_client,
            product=other_product,
            quantity=1,
            delivery_address='Санкт-Петербург, Невский, 1',
        )

        self.client.force_login(self.manager_user)
        response = self.client.get(reverse('orders:order_list'))

        self.assertContains(response, self.client_user.username)
        self.assertContains(response, self.other_client.username)
        self.assertContains(response, other_product.name)

    def test_client_can_create_order_for_self_only(self):
        self.client.force_login(self.client_user)
        response = self.client.post(reverse('orders:order_create'), {
            'product': self.product.pk,
            'quantity': 1,
            'delivery_address': 'Казань, ул. Баумана, д. 3',
            'comment': 'Позвонить перед доставкой',
        })

        self.assertRedirects(response, reverse('orders:order_list'))
        created_order = Order.objects.latest('id')
        self.assertEqual(created_order.customer, self.client_user)
        self.assertEqual(created_order.price_at_order, self.product.final_price)
