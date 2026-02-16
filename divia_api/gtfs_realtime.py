"""
Module pour récupérer les horaires temps réel via GTFS-RT
Remplace l'ancienne méthode totem() qui ne fonctionne plus
"""

import requests
from datetime import datetime
from google.transit import gtfs_realtime_pb2


class GTFSRealtimeAPI:
    """API pour récupérer les horaires temps réel via GTFS-RT de Divia"""
    
    TRIP_UPDATE_URL = "https://proxy.transport.data.gouv.fr/resource/divia-dijon-gtfs-rt-trip-update"
    VEHICLE_POSITION_URL = "https://proxy.transport.data.gouv.fr/resource/divia-dijon-gtfs-rt-vehicle-position"
    
    @staticmethod
    def _get_route_id(ligne_id):
        """
        Convertit un ID de ligne TOTEM en route_id GTFS
        
        Mappings découverts via analyse du flux GTFS-RT:
        - Lignes Lianes (L5, L6, L8, etc.) → 4-L{X}
        - Lignes Corol (B12, B13, etc.) → 4-{numéro}
        - Trams → 4-T1, 4-T2
        """
        # Mapping explicite pour les codes TOTEM connus
        mappings = {
            # === TRAMS ===
            "101": "4-T1",   # T1
            "202": "4-T2",   # T2 (à confirmer)
            
            # === LIGNES LIANES ===
            "87": "4-L5",    # L5 (plusieurs variantes, toutes sur route 4-L5)
            "88": "4-L5",    # L5 variante Université (même route GTFS)
            "89": "4-L6",    # L6
            "90": "4-L6",    # L6 variante Toison (même route GTFS)
            "91": "4-L8",    # L8
            "99": "4-L8",    # L8 variante ST-APOLLINAIRE (même route GTFS)
            "100": "4-L8",   # L8 variante Chicago (même route GTFS)
            "105": "4-L5",   # L5 (format alternatif)
            "106": "4-L6",   # L6 (format alternatif)
            "108": "4-L8",   # L8 (format alternatif)
            
            # === BUS COROL (B10-B19) ===
            "102": "4-12",   # B12
            "103": "4-13",   # B13
            "104": "4-14",   # B14
            "107": "4-15",   # B15
            "111": "4-16",   # B16
            "118": "4-18",   # B18
            "119": "4-19",   # B19
            
            # === AUTRES BUS (30-45) ===
            "30": "4-30",
            "31": "4-31",
            "32": "4-32",
            "33": "4-33",
            "34": "4-34",
            "35": "4-35",
            "36": "4-36",
            "37": "4-37",
            "38": "4-38",
            "40": "4-40",
            "41": "4-41",
            "42": "4-42",
            "43": "4-43",
            "44": "4-44",
            "45": "4-45",
            
            # === NAVETTES ===
            "CITY": "4-CITY",  # Navette City
            "CO": "4-CO",      # Flexo (à la demande)
            
            # === PROXILIANES (si disponibles) ===
            "139": "4-PL",     # ProxiLiane République (route exacte à confirmer)
            "140": "4-PL",     # ProxiLiane Université (route exacte à confirmer)
        }
        
        if ligne_id in mappings:
            return mappings[ligne_id]
        
        # Par défaut, essayer le format direct
        return f"4-{ligne_id}"
    
    @staticmethod
    def _get_stop_id(arret_code):
        """Convertit un code d'arrêt TOTEM en stop_id GTFS"""
        # Format: "4-{code}"
        return f"4-{arret_code}"
    
    @staticmethod
    def get_next_departures(ligne_id, arret_code, limit=2, timeout=15):
        """
        Récupère les prochains départs pour une ligne et un arrêt donnés
        
        Args:
            ligne_id (str): ID de la ligne (ex: "102" pour B12)
            arret_code (str): Code de l'arrêt (ex: "141" pour Wilson Carnot)
            limit (int): Nombre de prochains passages à retourner
            timeout (int): Timeout de la requête HTTP en secondes
        
        Returns:
            list: Liste de dict avec les informations de passage
                  Format: [{'time': datetime, 'minutes': int, 'formatted': str}, ...]
        """
        route_id = GTFSRealtimeAPI._get_route_id(ligne_id)
        stop_id = GTFSRealtimeAPI._get_stop_id(arret_code)
        
        try:
            # Récupération du flux GTFS-RT
            response = requests.get(GTFSRealtimeAPI.TRIP_UPDATE_URL, timeout=timeout)
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
                                timestamp = None
                                if stu.HasField('departure'):
                                    timestamp = stu.departure.time
                                elif stu.HasField('arrival'):
                                    timestamp = stu.arrival.time
                                
                                if timestamp:
                                    departure_time = datetime.fromtimestamp(timestamp)
                                    
                                    # Ajouter seulement les passages futurs
                                    if departure_time > now:
                                        minutes = int((departure_time - now).total_seconds() / 60)
                                        departures.append({
                                            'time': departure_time,
                                            'minutes': minutes,
                                            'formatted': departure_time.strftime("%H:%M")
                                        })
            
            # Trier par heure et limiter
            departures.sort(key=lambda x: x['time'])
            return departures[:limit]
            
        except requests.RequestException as e:
            print(f"Erreur réseau lors de la récupération GTFS-RT: {e}")
            return []
        except Exception as e:
            print(f"Erreur lors du traitement GTFS-RT: {e}")
            return []
    
    @staticmethod
    def get_vehicle_positions(ligne_id=None, timeout=10):
        """
        Récupère les positions en temps réel des véhicules
        
        Args:
            ligne_id (str, optional): ID de la ligne pour filtrer (ex: "102")
            timeout (int): Timeout de la requête HTTP en secondes
        
        Returns:
            list: Liste de dict avec les positions des véhicules
        """
        try:
            response = requests.get(GTFSRealtimeAPI.VEHICLE_POSITION_URL, timeout=timeout)
            response.raise_for_status()
            
            feed = gtfs_realtime_pb2.FeedMessage()
            feed.ParseFromString(response.content)
            
            vehicles = []
            route_id = GTFSRealtimeAPI._get_route_id(ligne_id) if ligne_id else None
            
            for entity in feed.entity:
                if entity.HasField('vehicle'):
                    veh = entity.vehicle
                    
                    # Filtrer par ligne si demandé
                    if route_id and veh.HasField('trip'):
                        if veh.trip.route_id != route_id:
                            continue
                    
                    vehicle_info = {}
                    
                    if veh.HasField('trip'):
                        vehicle_info['trip_id'] = veh.trip.trip_id
                        vehicle_info['route_id'] = veh.trip.route_id
                    
                    if veh.HasField('position'):
                        vehicle_info['latitude'] = veh.position.latitude
                        vehicle_info['longitude'] = veh.position.longitude
                        vehicle_info['speed'] = veh.position.speed if veh.position.HasField('speed') else None
                    
                    if veh.HasField('current_stop_sequence'):
                        vehicle_info['stop_sequence'] = veh.current_stop_sequence
                    
                    vehicles.append(vehicle_info)
            
            return vehicles
            
        except Exception as e:
            print(f"Erreur lors de la récupération des positions: {e}")
            return []


def get_next_buses(ligne_id, arret_code, count=2):
    """
    Fonction utilitaire compatible avec l'ancienne API totem()
    
    Args:
        ligne_id (str): ID de la ligne (ex: "102")
        arret_code (str): Code de l'arrêt (ex: "141")
        count (int): Nombre de passages à récupérer
    
    Returns:
        dict: Format compatible avec l'ancien totem()
              {"prochain_bus": "HH:MM", "suivant_bus": "HH:MM"}
    """
    departures = GTFSRealtimeAPI.get_next_departures(ligne_id, arret_code, limit=count)
    
    result = {}
    
    if len(departures) >= 1:
        result['prochain_bus'] = departures[0]['formatted']
        result['minutes_prochain'] = departures[0]['minutes']
    else:
        result['prochain_bus'] = "N/A"
        result['minutes_prochain'] = None
    
    if len(departures) >= 2:
        result['suivant_bus'] = departures[1]['formatted']
        result['minutes_suivant'] = departures[1]['minutes']
    else:
        result['suivant_bus'] = "N/A"
        result['minutes_suivant'] = None
    
    return result


if __name__ == "__main__":
    # Test du module
    print("Test du module gtfs_realtime\n")
    
    # Test ligne B12, arrêt Wilson Carnot
    print("Ligne B12 (102) - Arrêt Wilson Carnot (141)")
    result = get_next_buses("102", "141")
    print(f"  Prochain: {result['prochain_bus']} (dans {result['minutes_prochain']} min)")
    print(f"  Suivant:  {result['suivant_bus']} (dans {result['minutes_suivant']} min)")
    
    print("\nTest avec API directe:")
    departures = GTFSRealtimeAPI.get_next_departures("102", "141", limit=3)
    for i, dep in enumerate(departures, 1):
        print(f"  {i}. {dep['formatted']} (dans {dep['minutes']} min)")
    
    print("\nTest positions véhicules ligne B12:")
    vehicles = GTFSRealtimeAPI.get_vehicle_positions("102")
    print(f"  {len(vehicles)} véhicule(s) en circulation")
    for veh in vehicles[:3]:
        if 'latitude' in veh:
            print(f"    Position: {veh['latitude']:.4f}, {veh['longitude']:.4f}")
