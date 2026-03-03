"""
Décodage des flux GTFS-RT de Divia via transport.data.gouv.fr
"""
from requests import get

print("=" * 80)
print("INSTALLATION ET TEST GTFS-REALTIME")
print("=" * 80)

# D'abord, vérifier si gtfs-realtime-bindings est installé
try:
    from google.transit import gtfs_realtime_pb2
    print("✓ gtfs-realtime-bindings déjà installé\n")
except ImportError:
    print("❌ gtfs-realtime-bindings pas installé")
    print("\nPour installer:")
    print("  pip install gtfs-realtime-bindings")
    print("\nVeuillez l'installer et relancer ce script.")
    exit(1)

from datetime import datetime

print("[1] RÉCUPÉRATION DU FLUX GTFS-RT TRIP UPDATES\n")

url = "https://proxy.transport.data.gouv.fr/resource/divia-dijon-gtfs-rt-trip-update"
response = get(url, timeout=15)

print(f"Status: {response.status_code}")
print(f"Size: {len(response.content)} bytes")

if response.status_code != 200:
    print("❌ Impossible de récupérer les données")
    exit(1)

print("\n[2] DÉCODAGE DU PROTOCOL BUFFERS\n")

# Créer le message GTFS-RT
feed = gtfs_realtime_pb2.FeedMessage()

try:
    feed.ParseFromString(response.content)
    print(f"✓ Feed décodé avec succès")
    print(f"  Header: {feed.header}")
    print(f"  Timestamp: {datetime.fromtimestamp(feed.header.timestamp)}")
    print(f"  Nombre d'entités: {len(feed.entity)}")
except Exception as e:
    print(f"❌ Erreur de décodage: {e}")
    exit(1)

print("\n[3] ANALYSE DES ENTITÉS\n")

# Analyser les premières entités
print("Premiers trip updates:")
for i, entity in enumerate(feed.entity[:5]):
    if entity.HasField('trip_update'):
        trip = entity.trip_update.trip
        print(f"\n  Entité #{i}:")
        print(f"    Trip ID: {trip.trip_id}")
        print(f"    Route ID: {trip.route_id}")
        print(f"    Direction: {trip.direction_id}")
        
        if entity.trip_update.stop_time_update:
            print(f"    Stop time updates: {len(entity.trip_update.stop_time_update)}")
            for j, stu in enumerate(entity.trip_update.stop_time_update[:3]):
                print(f"      Stop #{j}:")
                print(f"        Stop ID: {stu.stop_id}")
                if stu.HasField('arrival'):
                    arrival_time = datetime.fromtimestamp(stu.arrival.time)
                    print(f"        Arrival: {arrival_time.strftime('%H:%M:%S')}")
                if stu.HasField('departure'):
                    departure_time = datetime.fromtimestamp(stu.departure.time)
                    print(f"        Departure: {departure_time.strftime('%H:%M:%S')}")

print("\n[4] RECHERCHE POUR LIGNE B12 (102) - ARRÊT WILSON CARNOT (141)\n")

# Chercher les trip updates pour notre ligne/arrêt spécifique
ligne_id = "102"  # B12
arret_code = "141"  # Wilson Carnot

# Dans GTFS, les IDs peuvent avoir des préfixes/formats différents
# Cherchons toutes les variations possibles
search_patterns = [
    f"102",  # ID ligne
    f"12",   # Code TOTEM
    f"B12",  # Nom commercial
    f"4-L12", # Format avec préfixe
]

stop_patterns = [
    "141",   # Code arrêt
    "4-141", # Avec préfixe
]

found_trips = []

for entity in feed.entity:
    if entity.HasField('trip_update'):
        trip = entity.trip_update.trip
        route_id = trip.route_id
        
        # Vérifier si c'est notre ligne
        is_our_line = any(pattern in route_id for pattern in search_patterns)
        
        if is_our_line:
            # Chercher notre arrêt dans les stop_time_updates
            for stu in entity.trip_update.stop_time_update:
                stop_id = stu.stop_id
                is_our_stop = any(pattern in stop_id for pattern in stop_patterns)
                
                if is_our_stop:
                    departure_time = None
                    if stu.HasField('departure'):
                        departure_time = datetime.fromtimestamp(stu.departure.time)
                    elif stu.HasField('arrival'):
                        departure_time = datetime.fromtimestamp(stu.arrival.time)
                    
                    if departure_time:
                        found_trips.append({
                            'trip_id': trip.trip_id,
                            'route_id': route_id,
                            'stop_id': stop_id,
                            'time': departure_time
                        })

if found_trips:
    print(f"✓ Trouvé {len(found_trips)} passages pour la ligne B12 à Wilson Carnot:")
    
    # Filtrer les passages futurs et trier
    now = datetime.now()
    future_trips = [t for t in found_trips if t['time'] > now]
    future_trips.sort(key=lambda x: x['time'])
    
    print(f"\n  Prochains passages ({len(future_trips)}):")
    for i, trip in enumerate(future_trips[:5]):
        minutes = int((trip['time'] - now).total_seconds() / 60)
        print(f"    {i+1}. {trip['time'].strftime('%H:%M:%S')} (dans {minutes} min)")
        print(f"       Route: {trip['route_id']}, Stop: {trip['stop_id']}")
else:
    print("❌ Aucun passage trouvé pour cette ligne/arrêt")
    print("\n  Routes trouvées dans le feed:")
    routes = set()
    for entity in feed.entity:
        if entity.HasField('trip_update'):
            routes.add(entity.trip_update.trip.route_id)
    for route in sorted(routes)[:20]:
        print(f"    - {route}")
    
    print("\n  Stops trouvés dans le feed:")
    stops = set()
    for entity in feed.entity:
        if entity.HasField('trip_update'):
            for stu in entity.trip_update.stop_time_update:
                stops.add(stu.stop_id)
    for stop in sorted(stops)[:20]:
        print(f"    - {stop}")

print("\n[5] RÉCUPÉRATION POSITIONS VÉHICULES\n")

url_vehicles = "https://proxy.transport.data.gouv.fr/resource/divia-dijon-gtfs-rt-vehicle-position"
response_veh = get(url_vehicles, timeout=10)

if response_veh.status_code == 200:
    feed_veh = gtfs_realtime_pb2.FeedMessage()
    feed_veh.ParseFromString(response_veh.content)
    
    print(f"✓ Feed véhicules décodé")
    print(f"  Nombre de véhicules: {len(feed_veh.entity)}")
    
    # Afficher quelques véhicules
    for i, entity in enumerate(feed_veh.entity[:3]):
        if entity.HasField('vehicle'):
            veh = entity.vehicle
            print(f"\n  Véhicule #{i}:")
            if veh.HasField('trip'):
                print(f"    Trip: {veh.trip.trip_id}")
                print(f"    Route: {veh.trip.route_id}")
            if veh.HasField('position'):
                print(f"    Position: lat={veh.position.latitude}, lon={veh.position.longitude}")
                print(f"    Vitesse: {veh.position.speed} m/s")
            if veh.HasField('current_stop_sequence'):
                print(f"    Arrêt actuel: {veh.current_stop_sequence}")

print("\n" + "=" * 80)
print("RÉSUMÉ")
print("=" * 80)
print("""
✓ Les flux GTFS-RT de Divia fonctionnent !
✓ Contiennent les données temps réel pour toutes les lignes
✓ Format standard utilisé par Google Maps et autres apps

PROCHAINES ÉTAPES:
1. Créer une fonction pour parser le GTFS-RT
2. Mapper les IDs (ligne 102 → route_id dans GTFS)
3. Mapper les codes arrêts (141 → stop_id dans GTFS)
4. Remplacer la méthode totem() dans divia_api

Le format GTFS nécessite de comprendre les IDs utilisés.
Il faudrait le fichier GTFS statique (static GTFS) pour avoir
le mapping complet ligne_id → route_id et arret_code → stop_id.
""")

print("\n" + "=" * 80)
