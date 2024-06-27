import csv
from django.core.management.base import BaseCommand, CommandError
from model.models import Constituency

class Command(BaseCommand):
    help = 'Import constituency data from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', help='Path to the CSV file')
    
    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        try:
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    for key in row:
                        if row[key] == '':
                            row[key] = None
                        else:
                            row[key] = row[key].strip('%')
                    constituency_id = row.get('id')
                    Constituency.objects.update_or_create(id=constituency_id, defaults=row)
            self.stdout.write(self.style.SUCCESS('Successfully imported data'))
        except FileNotFoundError:
            raise CommandError(f'File "{csv_file}" does not exist')
        except Exception as e:
            raise CommandError(f'An error occurred: {str(e)}')