from django.core.management.base import BaseCommand
from model.models import Constituency, Projection

class Command(BaseCommand):
    help = 'Remove unused projections from the database'

    def handle(self, *args, **kwargs):
        projections = Projection.objects.all()
        used_projections = set(Constituency.objects.filter(basic_projection__isnull=False).values_list('basic_projection', flat=True)).union(set(Constituency.objects.filter(detailed_projection__isnull=False).values_list('detailed_projection', flat=True)))
        unused_projections = projections.exclude(id__in=used_projections)
        count, _ = unused_projections.delete()
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {str(count)} unused projections'))
