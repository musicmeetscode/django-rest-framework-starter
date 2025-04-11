from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from accounts.models import CustomUser
class Command(BaseCommand):
    help="Creates a superuser if doesn't already exist"
    def handle(self, *args, **kwargs):
        User=get_user_model()
        email="nahabwe.edwin12@gmail.com"
        password="Admin@2024"
        user, created = CustomUser.objects.update_or_create(
            email=email,
            defaults={
                'email': email,
                'is_staff': True,
                'is_admin': True,
                'is_superuser': True,
                'full_name':"Super Admin User",

            }
        )
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Superuser  created successfully.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Superuser  updated successfully.'))
