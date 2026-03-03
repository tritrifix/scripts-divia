"""
Script pour découvrir les mappings exacts en testant différentes lignes
"""

from divia_api.gtfs_realtime import GTFSRealtimeAPI

# IDs à tester selon les scripts
test_cases = [
    ("87", "141", "L5 talant → Wilson Carnot"),
    ("87", "748", "L5 talant → Transvaal"),
    ("87", "1367", "L5 talant → Agrosup"),
    ("88", "322", "L5 univ → Baudin"),
    ("90", "141", "L6 toison → Wilson Carnot"),
    ("99", "141", "L8 ST-APOLLINAIRE → Wilson Carnot"),
    ("100", "322", "L8 chicago → Baudin"),
    ("139", "141", "ProxiLiane République → Wilson Carnot"),
    ("140", "322", "ProxiLiane Université → Baudin"),
]

print("Test des mappings actuels:\n")

for ligne_id, arret_code, description in test_cases:
    route_id = GTFSRealtimeAPI._get_route_id(ligne_id)
    stop_id = GTFSRealtimeAPI._get_stop_id(arret_code)
    deps = GTFSRealtimeAPI.get_next_departures(ligne_id, arret_code, limit=1)
    
    status = "✓" if deps else "✗"
    result = deps[0]['formatted'] if deps else "Aucun"
    
    print(f"{status} {description}")
    print(f"   Ligne {ligne_id} → Route {route_id}")
    print(f"   Arrêt {arret_code} → Stop {stop_id}")
    print(f"   Résultat: {result}\n")

# Maintenant cherchons dans le flux GTFS toutes les routes passant par Wilson Carnot (4-141)
print("\n" + "="*80)
print("RECHERCHE DANS LE FLUX GTFS")
print("="*80 + "\n")

import requests
from google.transit import gtfs_realtime_pb2

url = "https://proxy.transport.data.gouv.fr/resource/divia-dijon-gtfs-rt-trip-update"
response = requests.get(url, timeout=15)
feed = gtfs_realtime_pb2.FeedMessage()
feed.ParseFromString(response.content)

# Chercher les routes pour chaque arrêt problématique
stops_to_check = {
    "4-141": "Wilson Carnot",
    "4-322": "Baudin",
    "4-748": "Transvaal",
    "4-1367": "Agrosup",
}

for stop_id, stop_name in stops_to_check.items():
    routes_at_stop = set()
    
    for entity in feed.entity:
        if entity.HasField('trip_update'):
            trip = entity.trip_update.trip
            for stu in entity.trip_update.stop_time_update:
                if stu.stop_id == stop_id:
                    routes_at_stop.add(trip.route_id)
    
    print(f"\nArrêt {stop_name} ({stop_id}):")
    for route in sorted(routes_at_stop):
        print(f"  - {route}")
