import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create a superuser if it does not exist'

    def handle(self, *args, **kwargs):
        susername = os.getenv('DJANGO_SUPERUSERNAME')
        semail = os.getenv('DJANGO_SUPERUSER_EMAIL')
        spassword = os.getenv('DJANGO_SUPERUSER_PASSWORD')

        if not susername or not semail or not spassword:
            self.stdout.write(self.style.WARNING('Environment variables not set correctly.'))
            return

        if not User.objects.filter(username=susername).exists():
            User.objects.create_superuser(username=susername, email=semail, password=spassword)
            self.stdout.write(self.style.SUCCESS(f'Superuser "{susername}" created.'))
        else:
            self.stdout.write(self.style.WARNING(f'Superuser "{susername}" already exists.'))
