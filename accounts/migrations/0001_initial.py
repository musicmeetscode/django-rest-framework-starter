# Generated by Django 5.2 on 2025-04-11 08:01

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(blank=True, max_length=200, null=True, unique=True, verbose_name='email')),
                ('full_name', models.CharField(blank=True, max_length=150, null=True, verbose_name='Full Name')),
                ('phone', models.CharField(blank=True, max_length=50, null=True, unique=True)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='user_images/')),
                ('address', models.TextField(blank=True, null=True)),
                ('verify_code', models.TextField(blank=True, null=True)),
                ('is_verified', models.BooleanField(default=False)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_superuser', models.BooleanField(default=False)),
                ('is_admin', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
                ('auth_id', models.TextField(blank=True, null=True)),
                ('auth_provider', models.CharField(default='email', max_length=255)),
                ('status', models.CharField(choices=[('active', 'Active user'), ('inactive', 'User Inactive'), ('deleted', 'Soft Delete user')], default='active', max_length=32)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name_plural': 'users',
            },
        ),
    ]
