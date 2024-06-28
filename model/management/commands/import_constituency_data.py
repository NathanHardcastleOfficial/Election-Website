import csv
from django.core.management.base import BaseCommand, CommandError
from model.models import Constituency, Projection
from model.stats import voteshare, updateTotals

class Command(BaseCommand):
    help = 'Import constituency data from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', help='Path to the CSV file')
    
    def handle(self, *args, **kwargs):
        party_strenth_columns = {'base_con': 'con', 'base_lab': 'lab', 'base_ld': 'ld', 'base_ref': 'ref', 'base_grn': 'grn', 'base_snp': 'snp', 'base_pc': 'pc', 'base_min': 'min'}
        party_capitalisations = {'con': 'Con', 'lab': 'Lab', 'ld': 'LD', 'ref': 'Ref', 'grn': 'Grn', 'snp': 'SNP', 'pc': 'PC', 'min': 'Oth'}
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
                    strengths = {}
                    for column, party in party_strenth_columns.items():
                        if row[column] != None:
                            strengths[party] = row[column]
                    basic_projection = voteshare(strengths)
                    basic_projection['detailed'] = False
                    basic_projection['winner'] = party_capitalisations[max(basic_projection, key=basic_projection.get)]
                    basic_projection = Projection(**basic_projection)
                    basic_projection.save()
                    row['basic_projection'] = basic_projection
                    constituency_id = row.get('id')
                    Constituency.objects.update_or_create(id=constituency_id, defaults=row)
                updateTotals()
            self.stdout.write(self.style.SUCCESS('Successfully imported data'))
        except FileNotFoundError:
            raise CommandError(f'File "{csv_file}" does not exist')
        except Exception as e:
            raise CommandError(f'An error occurred: {str(e)}')