import shapefile
from shapely.geometry import Point, shape

# Load shapefile
sf = shapefile.Reader(r"C:\Users\highe\OneDrive\Desktop\Capstone Project\Village level boundary\RWA_adm5.shp")

# Example point -1.3782236289913914, 29.80943005549639
latitude = -1.3782236289913914
longitude =29.80943005549639
point = Point(longitude, latitude)

village_info = None

for record, shp in zip(sf.records(), sf.shapes()):
    polygon = shape(shp.__geo_interface__)
    if polygon.contains(point):
        village_info = {
            "province": record[4],
            "district": record[6],
            "sector": record[8],
            "cell": record[10],
            "village": record[12]
        }
        break

if village_info:
    print("Point is located in:")
    print(f"Province: {village_info['province']}")
    print(f"District: {village_info['district']}")
    print(f"Sector: {village_info['sector']}")
    print(f"Cell: {village_info['cell']}")
    print(f"Village: {village_info['village']}")
else:
    print("Point is not inside any village polygon.")
