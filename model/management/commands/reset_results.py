from django.core.management.base import BaseCommand
from model.models import Result
from model.stats import doBasicProjection

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        confirmation = input("Are you sure you want to delete all results? ")
        if confirmation.lower() in ('yes','y'):
            results = Result.objects.all()
            count, _ = results.delete()
            doBasicProjection()
            self.stdout.write(self.style.SUCCESS(f'Successfully deleted {str(count)} results'))
        else:
            self.stdout.write(self.style.WARNING('Operation cancelled. No results were deleted.'))