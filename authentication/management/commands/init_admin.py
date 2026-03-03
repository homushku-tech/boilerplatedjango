from django.conf import settings
from django.core.management.base import BaseCommand
from authentication.models import CustomUser

class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            if CustomUser.objects.filter(username='admin').exists():
                print('Admin acc already exists')
                return
            username = 'admin'
            email = 'admin@admin.admin'
            password = 'admin'
            admin = CustomUser.objects.create_superuser(email=email, username=username, password=password)
            admin.is_active = True
            admin.is_admin = True
            admin.save()
            print('Admin acc create successfully')
        except Exception as e:
            print(f'Admin acc creating FAIL. \n '
                  f'Exception: {e}')