"""
Script pour découvrir tous les route_ids disponibles dans le flux GTFS-RT
et créer le mapping complet ligne TOTEM → route_id GTFS
"""

import requests
from google.transit import gtfs_realtime_pb2
from collections import defaultdict

url = "https://proxy.transport.data.gouv.fr/resource/divia-dijon-gtfs-rt-trip-update"

print("Récupération du flux GTFS-RT...")
response = requests.get(url, timeout=15)
feed = gtfs_realtime_pb2.FeedMessage()
feed.ParseFromString(response.content)

# Collecter tous les route_ids
routes = set()
route_info = defaultdict(lambda: {"stops": set(), "trips": set()})

for entity in feed.entity:
    if entity.HasField('trip_update'):
        trip = entity.trip_update.trip
        route_id = trip.route_id
        routes.add(route_id)
        route_info[route_id]["trips"].add(trip.trip_id)
        
        for stu in entity.trip_update.stop_time_update:
            route_info[route_id]["stops"].add(stu.stop_id)

print(f"\nTrouvé {len(routes)} routes dans le flux GTFS-RT\n")
print("=" * 80)
print("ROUTES DISPONIBLES")
print("=" * 80)

for route_id in sorted(routes):
    info = route_info[route_id]
    print(f"\nRoute ID: {route_id}")
    print(f"  Trips: {len(info['trips'])}")
    print(f"  Stops: {len(info['stops'])}")
    
    # Essayer de déduire le code TOTEM
    # Pattern: "4-{code}"
    if route_id.startswith("4-"):
        code = route_id[2:]  # Enlever "4-"
        
        # Deviner le code TOTEM
        if code.startswith("T"):  # Tram
            print(f"  Type: TRAM {code}")
            if code == "T1":
                totem_guess = "101"
            elif code == "T2":
                totem_guess = "???"
            else:
                totem_guess = "???"
        elif code.isdigit():  # Bus numérique
            ligne_num = int(code)
            if ligne_num  >= 10:  # B11, B12, B13, etc.
                totem_guess = f"10{ligne_num % 10}"  # B12 → 102
            elif ligne_num < 10:  # L5, L6, L8, etc.
                totem_guess = f"10{ligne_num}"  # L5 → 105
            else:
                totem_guess = "???"
            print(f"  Type: BUS Ligne {code}")
        else:
            print(f"  Type: Autre ({code})")
            totem_guess = "???"
        
        print(f"  Code TOTEM estimé: {totem_guess}")

print("\n" + "=" * 80)
print("MAPPING SUGGÉRÉ POUR gtfs_realtime.py")
print("=" * 80)
print("""
mappings = {
    # Trams
    "101": "4-T1",   # Tram T1
    
    # Bus Lianes (format original découvert)
    "105": "4-5",    # L5
    "106": "4-6",    # L6
    "108": "4-8",    # L8
    
    # Bus Corol
    "102": "4-12",   # B12
    "103": "4-13",   # B13
    # ... ajoutez les autres selon vos besoins
}
""")

print("\n" + "=" * 80)
print("ARRÊTS POPULAIRES")
print("=" * 80)

# Compter la fréquence des arrêts
stop_counts = defaultdict(int)
for info in route_info.values():
    for stop in info["stops"]:
        stop_counts[stop] += 1

print("\n20 arrêts les plus fréquents:")
for stop_id, count in sorted(stop_counts.items(), key=lambda x: x[1], reverse=True)[:20]:
    # Extraire le code TOTEM
    if stop_id.startswith("4-"):
        totem_code = stop_id[2:]
        print(f"  Stop GTFS: {stop_id:15s} (TOTEM: {totem_code:5s}) - {count} routes")
    else:
        print(f"  Stop GTFS: {stop_id:15s} - {count} routes")

print("\n" + "=" * 80)
print("VÉRIFICATION ARRÊT WILSON CARNOT (141)")
print("=" * 80)

wilson_stops = [s for s in stop_counts.keys() if "141" in s]
print(f"\nArrêts contenant '141': {wilson_stops}")

if "4-141" in stop_counts:
    print(f"\n✓ Arrêt 4-141 (Wilson Carnot) trouvé!")
    print(f"  Desservi par {stop_counts['4-141']} routes")
    
    print("\n  Routes passant à Wilson Carnot:")
    for route_id in sorted(routes):
        if "4-141" in route_info[route_id]["stops"]:
            print(f"    - {route_id}")
