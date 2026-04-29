from django.contrib.auth.models import Group, User
from django.test import TestCase

from .roles import get_user_role


class RoleResolutionTests(TestCase):
    def test_guest_role_for_anonymous_user(self):
        self.assertEqual(get_user_role(None), 'guest')

    def test_client_role_from_group(self):
        user = User.objects.create_user('client', password='pass12345')
        group, _ = Group.objects.get_or_create(name='Клиенты')
        user.groups.add(group)

        self.assertEqual(get_user_role(user), 'client')

    def test_manager_role_has_priority_over_client(self):
        user = User.objects.create_user('manager', password='pass12345')
        client_group, _ = Group.objects.get_or_create(name='Клиенты')
        manager_group, _ = Group.objects.get_or_create(name='Менеджеры')
        user.groups.add(client_group, manager_group)

        self.assertEqual(get_user_role(user), 'manager')

    def test_admin_role_for_superuser(self):
        user = User.objects.create_superuser('admin', 'admin@example.com', 'pass12345')

        self.assertEqual(get_user_role(user), 'admin')
