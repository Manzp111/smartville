from django.core.management.base import BaseCommand
from Location.models import Location
import shapefile

class Command(BaseCommand):
    help = "Load all villages from shapefile into Location model"

    def handle(self, *args, **kwargs):
        sf = shapefile.Reader(r"Village level boundary\RWA_adm5.shp")
        for record in sf.records():
            Location.objects.get_or_create(
                province=record['NAME_1'],
                district=record['NAME_2'],
                sector=record['NAME_3'],
                cell=record['NAME_4'],
                village=record['NAME_5']
            )
        self.stdout.write(self.style.SUCCESS("All villages loaded successfully!"))
