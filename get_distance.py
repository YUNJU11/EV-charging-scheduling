import requests
import json

def Get_distance_osm(coord1, coord2):
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    r = requests.get(
        f"http://router.project-osrm.org/route/v1/car/{lon1},{lat1};{lon2},{lat2}?overview=full""")
    routes = json.loads(r.content)
    route_1 = routes.get("routes")[0]
    dist = route_1["distance"]

    return dist/1000  # Returns in kilometers