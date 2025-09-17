from django.core.management.base import BaseCommand
from Village.models import Village
import shapefile

class Command(BaseCommand):
    help = "Load all villages from shapefile into Village model"

    def handle(self, *args, **kwargs):
        try:
            sf = shapefile.Reader(r"Village level boundary\RWA_adm5.shp")
            records=sf.records()
            start_id=0
            for i,record in enumerate(records[start_id:],start=start_id):
                Village, created = Village.objects.get_or_create(
                    province=record['NAME_1'],
                    district=record['NAME_2'],
                    sector=record['NAME_3'],
                    cell=record['NAME_4'],
                    village=record['NAME_5']
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created Village: {Village.village}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Village already exists: {Village.village}"))
            self.stdout.write(self.style.SUCCESS("All villages loaded successfully!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error loading villages: {str(e)}"))