from shapely.geometry import Point, shape
from .models import Village

def get_location_info(latitude, longitude):
    point = Point(longitude, latitude)  # shapely uses (lon, lat)

    for village in Village.objects.all():
        polygon = shape(village.geom)  # convert GeoJSON to Polygon
        if polygon.contains(point):
            return {
                "village": village.name,
                "sector": village.sector,
                "district": village.district
            }
    
    return {
        "village": None,
        "sector": None,
        "district": None
    }
