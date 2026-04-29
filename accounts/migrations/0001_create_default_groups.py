from django.contrib.auth.models import Group
from django.db import migrations


def create_default_groups(apps, schema_editor):
    Group.objects.get_or_create(name='Клиенты')
    Group.objects.get_or_create(name='Менеджеры')


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(create_default_groups, migrations.RunPython.noop),
    ]
