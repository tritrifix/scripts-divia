#!/usr/bin/env python3
"""
Script pour récupérer les horaires temps réel de la ligne B12
entre Plombière d'Or et Wilson Carnot en utilisant le flux GTFS-RT
"""

import requests
from datetime import datetime
from google.transit import gtfs_realtime_pb2

def get_next_departures(route_id, stop_id, limit=2):
    """
    Récupère les prochains départs pour une ligne et un arrêt donnés
    
    Args:
        route_id: ID GTFS de la route (ex: "4-12" pour B12)
        stop_id: ID GTFS de l'arrêt (ex: "4-141" pour Wilson Carnot)
        limit: Nombre de prochains passages à retourner
    
    Returns:
        Liste de timestamps des prochains passages
    """
    url = "https://proxy.transport.data.gouv.fr/resource/divia-dijon-gtfs-rt-trip-update"
    
    try:
        # Récupération du flux GTFS-RT
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        # Décodage du Protocol Buffers
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
        
        # Recherche des passages
        departures = []
        now = datetime.now()
        
        for entity in feed.entity:
            if entity.HasField('trip_update'):
                trip = entity.trip_update.trip
                
                # Vérifier la ligne
                if trip.route_id == route_id:
                    # Chercher l'arrêt dans les stop_time_updates
                    for stu in entity.trip_update.stop_time_update:
                        if stu.stop_id == stop_id:
                            # Récupérer l'heure de départ
                            if stu.HasField('departure'):
                                timestamp = stu.departure.time
                            elif stu.HasField('arrival'):
                                timestamp = stu.arrival.time
                            else:
                                continue
                            
                            departure_time = datetime.fromtimestamp(timestamp)
                            
                            # Ajouter seulement les passages futurs
                            if departure_time > now:
                                departures.append(departure_time)
        
        # Trier et limiter
        departures.sort()
        return departures[:limit]
        
    except Exception as e:
        print(f"Erreur lors de la récupération des données: {e}")
        return []

def format_time(dt):
    """Formate un datetime en HH:MM"""
    if dt:
        return dt.strftime("%H:%M")
    return "N/A"

def main():
    print("=" * 60)
    print("HORAIRES TEMPS RÉEL - LIGNE B12")
    print("Arrêt: Wilson Carnot")
    print("=" * 60)
    
    # IDs GTFS
    route_id = "4-12"   # Ligne B12
    stop_id = "4-141"   # Arrêt Wilson Carnot
    
    # Récupération des prochains passages
    departures = get_next_departures(route_id, stop_id, limit=2)
    
    if len(departures) >= 2:
        prochain = departures[0]
        suivant = departures[1]
        
        now = datetime.now()
        minutes_prochain = int((prochain - now).total_seconds() / 60)
        minutes_suivant = int((suivant - now).total_seconds() / 60)
        
        print(f"\nProchain bus:  {format_time(prochain)} (dans {minutes_prochain} min)")
        print(f"Bus suivant:   {format_time(suivant)} (dans {minutes_suivant} min)")
        
        # Format JSON pour intégration
        result = {
            "ligne": "B12",
            "arret": "Wilson Carnot",
            "timestamp": datetime.now().isoformat(),
            "prochain_bus": format_time(prochain),
            "minutes_prochain": minutes_prochain,
            "suivant_bus": format_time(suivant),
            "minutes_suivant": minutes_suivant
        }
        
        print("\n" + "=" * 60)
        print("RÉSULTAT JSON:")
        print("=" * 60)
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    elif len(departures) == 1:
        prochain = departures[0]
        now = datetime.now()
        minutes = int((prochain - now).total_seconds() / 60)
        
        print(f"\nProchain bus:  {format_time(prochain)} (dans {minutes} min)")
        print("Bus suivant:   Aucune donnée")
        
        result = {
            "ligne": "B12",
            "arret": "Wilson Carnot",
            "timestamp": datetime.now().isoformat(),
            "prochain_bus": format_time(prochain),
            "minutes_prochain": minutes,
            "suivant_bus": "N/A",
            "minutes_suivant": None
        }
        
        print("\n" + "=" * 60)
        print("RÉSULTAT JSON:")
        print("=" * 60)
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    else:
        print("\n⚠ Aucun passage trouvé dans les prochaines heures")
        print("Vérifiez que la ligne est en service")
        
        result = {
            "ligne": "B12",
            "arret": "Wilson Carnot",
            "timestamp": datetime.now().isoformat(),
            "prochain_bus": "N/A",
            "suivant_bus": "N/A",
            "error": "Aucun passage trouvé"
        }
        
        print("\n" + "=" * 60)
        print("RÉSULTAT JSON:")
        print("=" * 60)
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    print("=" * 60)

if __name__ == "__main__":
    main()
