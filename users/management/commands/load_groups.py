from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Load moderator group from fixture'

    def handle(self, *args, **options):
        call_command('loaddata', 'groups.json')
        self.stdout.write(self.style.SUCCESS('Successfully loaded groups'))