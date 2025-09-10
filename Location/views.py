from django.shortcuts import render
import shapefile
from shapely.geometry import Point, shape


def locate_point(request):
    result = None

    if request.method == "POST":
        latitude = float(request.POST.get("latitude"))
        longitude = float(request.POST.get("longitude"))

        # Load shapefile
        # sf = shapefile.Reader(r"C:\Users\highe\OneDrive\Desktop\Capstone Project\Village_level_boundary\RWA_adm5.shp")
        sf = shapefile.Reader(r"C:\Users\highe\OneDrive\Desktop\Capstone Project\Village level boundary\RWA_adm5.shp")

        point = Point(longitude, latitude)

        for record, shp in zip(sf.records(), sf.shapes()):
            polygon = shape(shp.__geo_interface__)
            if polygon.contains(point):
                result = {
                    "province": record[4],
                    "district": record[6],
                    "sector": record[8],
                    "cell": record[10],
                    "village": record[12],
                }
                break

    return render(request, "home/home.html", {"result": result})
