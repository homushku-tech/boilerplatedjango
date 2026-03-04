from authentication.models import CustomUser
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self):
        try:
            if CustomUser.objects.filter(username="admin").exists():
                print("Admin acc already exists")
                return
            username = "admin"
            email = "admin@admin.admin"
            password = "admin"
            admin = CustomUser.objects.create_superuser(
                email=email, username=username, password=password
            )
            admin.is_active = True
            admin.is_admin = True
            admin.save()
            print("Admin acc create successfully")
        except Exception as e:
            print(f"Admin acc creating FAIL. \n Exception: {e}")
