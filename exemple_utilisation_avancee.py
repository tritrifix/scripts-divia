#!/usr/bin/env python3
"""
Exemple d'utilisation avancée de l'API GTFS-RT de Divia

Ce script montre comment utiliser toutes les fonctionnalités
du module gtfs_realtime pour obtenir des informations détaillées
sur les passages de bus, les positions des véhicules, etc.
"""

from divia_api.gtfs_realtime import GTFSRealtimeAPI, get_next_buses
from datetime import datetime

print("=" * 80)
print("EXEMPLE D'UTILISATION AVANCÉE - API GTFS-RT DIVIA")
print("=" * 80)

# ============================================================================
# 1. UTILISATION SIMPLE (compatible ancien totem())
# ============================================================================

print("\n[1] UTILISATION SIMPLE - Format compatible ancienne API\n")

lignes_test = [
    ("102", "141", "B12 à Wilson Carnot"),
    ("87", "141", "L5 à Wilson Carnot"),
    ("90", "141", "L6 à Wilson Carnot"),
]

for ligne_id, arret_code, description in lignes_test:
    result = get_next_buses(ligne_id, arret_code)
    print(f"{description}:")
    print(f"  Prochain: {result['prochain_bus']} (dans {result['minutes_prochain']} min)")
    print(f"  Suivant:  {result['suivant_bus']} (dans {result['minutes_suivant']} min)\n")

# ============================================================================
# 2. RÉCUPÉRATION DE PLUSIEURS PASSAGES
# ============================================================================

print("\n[2] RÉCUPÉRATION DE PLUSIEURS PASSAGES\n")

print("Prochains 5 passages de la ligne B12 à Wilson Carnot:\n")
departures = GTFSRealtimeAPI.get_next_departures("102", "141", limit=5)

for i, dep in enumerate(departures, 1):
    heure = dep['formatted']
    minutes = dep['minutes']
    timestamp = dep['time']
    
    status = ""
    if minutes == 0:
        status = " 🚌 À l'arrêt!"
    elif minutes <= 2:
        status = " ⏰ Imminent"
    elif minutes <= 5:
        status = " 🏃 Dépêchez-vous"
    
    print(f"  {i}. {heure} (dans {minutes} min){status}")
    print(f"     Timestamp: {timestamp.isoformat()}")

# ============================================================================
# 3. TOUTES LES LIGNES À UN ARRÊT
# ============================================================================

print("\n[3] TOUTES LES LIGNES À UN ARRÊT\n")

print("Prochains passages à Wilson Carnot (tous les bus):\n")

# Wilson Carnot est desservi par: B12, L5, L6, L8
lignes_wilson = [
    ("102", "B12"),
    ("87", "L5"),
    ("90", "L6"),
    ("99", "L8"),
]

tous_passages = []

for ligne_id, nom in lignes_wilson:
    deps = GTFSRealtimeAPI.get_next_departures(ligne_id, "141", limit=2)
    for dep in deps:
        tous_passages.append({
            'ligne': nom,
            'heure': dep['formatted'],
            'minutes': dep['minutes'],
            'time': dep['time']
        })

# Trier par heure de départ
tous_passages.sort(key=lambda x: x['time'])

for passage in tous_passages[:10]:  # Afficher les 10 prochains
    print(f"  {passage['ligne']:4s} - {passage['heure']} (dans {passage['minutes']} min)")

# ============================================================================
# 4. POSITIONS DES VÉHICULES EN TEMPS RÉEL
# ============================================================================

print("\n[4] POSITIONS DES VÉHICULES EN TEMPS RÉEL\n")

print("Position des bus B12 en circulation:\n")
vehicles_b12 = GTFSRealtimeAPI.get_vehicle_positions("102")

if vehicles_b12:
    print(f"  {len(vehicles_b12)} véhicule(s) en circulation\n")
    
    for i, veh in enumerate(vehicles_b12, 1):
        print(f"  Véhicule #{i}:")
        if 'trip_id' in veh:
            print(f"    Trip ID: {veh['trip_id']}")
        if 'latitude' in veh:
            lat, lon = veh['latitude'], veh['longitude']
            print(f"    Position: {lat:.6f}, {lon:.6f}")
            print(f"    Google Maps: https://www.google.com/maps?q={lat},{lon}")
        if 'speed' in veh and veh['speed']:
            vitesse_kmh = veh['speed'] * 3.6
            print(f"    Vitesse: {vitesse_kmh:.1f} km/h")
        if 'stop_sequence' in veh:
            print(f"    Arrêt actuel: #{veh['stop_sequence']}")
        print()
else:
    print("  Aucun véhicule B12 détecté en ce moment")

# ============================================================================
# 5. MONITORING EN CONTINU
# ============================================================================

print("\n[5] EXEMPLE DE MONITORING EN CONTINU\n")

print("Code pour surveiller un arrêt en continu:")
print()
print("  def monitor_arret(ligne_id, arret_code, interval=30):")
print("      '''Surveille un arrêt toutes les X secondes'''")
print("      import time")
print("      ")
print("      while True:")
print("          result = get_next_buses(ligne_id, arret_code)")
print("          now = datetime.now().strftime('%H:%M:%S')")
print("          ")
print("          print(f'[{now}] Prochain: {result[\"minutes_prochain\"]}min | '")
print("                f'Suivant: {result[\"minutes_suivant\"]}min')")
print("          ")
print("          # Alerte si bus proche")
print("          if isinstance(result['minutes_prochain'], int):")
print("              if result['minutes_prochain'] <= 3:")
print("                  print('  ALERTE: Bus arrive!')")
print("          ")
print("          time.sleep(interval)")
print()
print("  # Utilisation:")
print("  # monitor_arret('102', '141', interval=30)  # B12 à Wilson Carnot")
print()

# ============================================================================
# 6. EXPORT DES DONNÉES
# ============================================================================

print("\n[6] EXPORT DES DONNÉES\n")

print("Export JSON des prochains passages:\n")

import json

export_data = {
    "timestamp": datetime.now().isoformat(),
    "arret": "Wilson Carnot (141)",
    "lignes": []
}

for ligne_id, nom in lignes_wilson:
    deps = GTFSRealtimeAPI.get_next_departures(ligne_id, "141", limit=3)
    
    if deps:
        export_data["lignes"].append({
            "id": ligne_id,
            "nom": nom,
            "passages": [
                {
                    "heure": dep['formatted'],
                    "minutes": dep['minutes'],
                    "timestamp": dep['time'].isoformat()
                }
                for dep in deps
            ]
        })

print(json.dumps(export_data, indent=2, ensure_ascii=False))

# ============================================================================
# 7. CALCUL DE FRÉQUENCE
# ============================================================================

print("\n[7] CALCUL DE FRÉQUENCE\n")

print("Fréquence de passage (écart moyen entre deux bus):\n")

for ligne_id, nom in lignes_wilson:
    deps = GTFSRealtimeAPI.get_next_departures(ligne_id, "141", limit=5)
    
    if len(deps) >= 2:
        # Calculer les écarts
        ecarts = []
        for i in range(len(deps) - 1):
            ecart = (deps[i+1]['time'] - deps[i]['time']).total_seconds() / 60
            ecarts.append(ecart)
        
        freq_moyenne = sum(ecarts) / len(ecarts)
        freq_min = min(ecarts)
        freq_max = max(ecarts)
        
        print(f"  {nom}:")
        print(f"    Fréquence moyenne: {freq_moyenne:.1f} min")
        print(f"    Écart min: {freq_min:.1f} min")
        print(f"    Écart max: {freq_max:.1f} min\n")

# ============================================================================
# 8. GESTION DES ERREURS
# ============================================================================

print("\n[8] GESTION DES ERREURS\n")

print("Code avec gestion d'erreurs:")
print()
print("  def get_next_buses_safe(ligne_id, arret_code):")
print("      '''Version avec gestion d'erreurs'''")
print("      try:")
print("          result = get_next_buses(ligne_id, arret_code)")
print("          ")
print("          # Vérifier si des données sont disponibles")
print("          if result['minutes_prochain'] is None:")
print("              return {")
print("                  'status': 'no_data',")
print("                  'message': 'Aucun passage prévu'")
print("              }")
print("          ")
print("          return {'status': 'ok', 'data': result}")
print("          ")
print("      except Exception as e:")
print("          return {'status': 'error', 'message': str(e)}")
print()
print("  # Utilisation:")
print("  result = get_next_buses_safe('102', '141')")
print()
print("  if result['status'] == 'ok':")
print("      print(f\"Prochain bus: {result['data']['minutes_prochain']} min\")")
print("  elif result['status'] == 'no_data':")
print("      print('Aucune donnée disponible')")
print("  else:")
print("      print(f\"Erreur: {result['message']}\")")
print()

print("=" * 80)
print("FIN DES EXEMPLES")
print("=" * 80)
print("""
Pour plus d'informations:
- Voir MIGRATION_REUSSIE.md pour la documentation complète
- Voir divia_api/gtfs_realtime.py pour le code source
- Voir test_mappings.py pour tester les mappings
- Voir discover_gtfs_routes.py pour explorer le réseau

API utilisée: https://proxy.transport.data.gouv.fr/resource/divia-dijon-gtfs-rt-trip-update
Format: GTFS-RT (Protocol Buffers)
Standard: https://developers.google.com/transit/gtfs-realtime
""")
