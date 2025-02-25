from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Help message"

    def handle(self, *args, **options):
        print("Hello, World!")
