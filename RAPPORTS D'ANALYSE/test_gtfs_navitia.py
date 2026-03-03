"""
Test de Google Transit / GTFS Realtime
Google Maps utilise généralement GTFS-RT pour les données temps réel
"""
from requests import get
import json

print("=" * 80)
print("RECHERCHE DE FLUX GTFS REALTIME POUR DIVIA")
print("=" * 80)

# Google Transit Partner / GTFS-RT endpoints standards
gtfs_rt_urls = [
    # Format standard GTFS-RT
    ("GTFS-RT Trip Updates", "https://proxy.transport.data.gouv.fr/resource/divia-dijon-gtfs-rt-trip-update"),
    ("GTFS-RT Vehicle Pos", "https://proxy.transport.data.gouv.fr/resource/divia-dijon-gtfs-rt-vehicle-position"),
    ("GTFS-RT Alerts", "https://proxy.transport.data.gouv.fr/resource/divia-dijon-gtfs-rt-alerts"),
    
    # Divia direct
    ("Divia GTFS-RT 1", "https://www.divia.fr/gtfs-rt/trip-updates"),
    ("Divia GTFS-RT 2", "https://data.divia.fr/gtfs-rt/trip-updates"),
    ("Divia GTFS-RT 3", "https://bo-api.divia.fr/gtfs-rt/trip-updates"),
    
    # Navitia (système utilisé par Divia selon les URLs trouvées)
    ("Navitia Coverage", "https://api.navitia.io/v1/coverage/fr-bdx"),
    ("Navitia Dijon", "https://api.navitia.io/v1/coverage/fr-dijon"),
]

print("\n[1] TEST DES ENDPOINTS GTFS-RT\n")

for name, url in gtfs_rt_urls:
    try:
        # Essayer avec et sans authentification Navitia
        headers = {}
        if 'navitia' in url:
            # Navitia nécessite une clé API (on teste sans d'abord)
            pass
        
        response = get(url, headers=headers, timeout=5)
        print(f"{name}")
        print(f"  URL: {url}")
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"  ✓✓✓ ENDPOINT TROUVÉ!")
            content_type = response.headers.get('Content-Type', '')
            print(f"  Content-Type: {content_type}")
            print(f"  Size: {len(response.content)} bytes")
            
            # GTFS-RT est en Protocol Buffers, pas JSON
            if 'application/octet-stream' in content_type or 'protobuf' in content_type:
                print(f"  → Format GTFS-RT (Protocol Buffers)")
            elif 'json' in content_type:
                try:
                    data = response.json()
                    print(f"  → Format JSON")
                    print(f"  Keys: {list(data.keys()) if isinstance(data, dict) else 'Array'}")
                except:
                    pass
            
            print(f"  Preview: {response.content[:100]}")
        elif response.status_code == 401:
            print(f"  → Authentification requise")
        elif response.status_code == 404:
            pass  # Silent
        
        print()
        
    except Exception as e:
        if 'ConnectionError' not in str(type(e).__name__):
            print(f"{name}: {type(e).__name__}")

print("\n[2] RECHERCHE SUR TRANSPORT.DATA.GOUV.FR\n")

# Chercher Divia sur le portail national
search_urls = [
    "https://transport.data.gouv.fr/api/datasets?q=divia",
    "https://transport.data.gouv.fr/api/datasets?q=dijon",
]

for url in search_urls:
    try:
        response = get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"Recherche: {url}")
            print(f"  Résultats: {len(data) if isinstance(data, list) else 'N/A'}")
            
            if isinstance(data, list) and len(data) > 0:
                print(f"\n  Datasets trouvés:")
                for dataset in data[:5]:
                    if isinstance(dataset, dict):
                        print(f"    - {dataset.get('title', dataset.get('name', 'N/A'))}")
                        if 'resources' in dataset:
                            for resource in dataset.get('resources', [])[:3]:
                                if 'gtfs' in resource.get('format', '').lower() or 'real' in resource.get('title', '').lower():
                                    print(f"      → {resource.get('title', 'N/A')}: {resource.get('url', 'N/A')}")
            print()
    except Exception as e:
        print(f"Erreur: {e}")

print("\n[3] TEST DIRECT DES ENDPOINTS SIMILAIRES À L'ANCIEN\n")

# Le nouvel endpoint pourrait être similaire à l'ancien mais avec une structure différente
similar_endpoints = [
    ("New format 1", "POST", "https://www.divia.fr/bus-tram", {
        "type": "prochains-passages",
        "ligne": "102",
        "arret": "141"
    }),
    ("New format 2", "POST", "https://www.divia.fr/api/bus-tram/prochains-passages", {
        "ligne_id": "102",
        "arret_code": "141"
    }),
    ("New format 3", "GET", "https://www.divia.fr/api/v1/prochains-passages?ligne=102&arret=141", {}),
    ("New format 4", "GET", "https://www.divia.fr/api/lignes/102/arrets/141/prochains-passages", {}),
]

for name, method, url, data in similar_endpoints:
    try:
        if method == "POST":
            # Essayer JSON
            response = get(url, json=data, timeout=5) if method == "GET" else get(url, json=data, timeout=5)
            if response.status_code == 200 and len(response.content) < 50000:
                print(f"{name}")
                print(f"  {method} {url}")
                print(f"  ✓ Réponse reçue ({len(response.content)} bytes)")
        else:
            response = get(url, timeout=5)
            if response.status_code == 200 and len(response.content) < 50000:
                print(f"{name}")
                print(f"  {method} {url}")
                print(f"  ✓ Réponse reçue ({len(response.content)} bytes)")
    except:
        pass

print("\n[4] INFORMATION SUR NAVITIA\n")

print("""
Navitia est détecté dans les URLs de l'API horaires.
Navitia.io propose une API temps réel publique.

Pour tester Navitia:
1. Créer un compte sur https://www.navitia.io/
2. Obtenir une clé API gratuite
3. Tester: https://api.navitia.io/v1/coverage/fr-dijon/

Documentation: https://doc.navitia.io/
""")

print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)
print("""
Le site Divia utilise probablement:
- JavaScript moderne (SPA) qui charge les données après le chargement
- Possiblement un flux GTFS-RT non public
- Ou l'API Navitia (nécessite une clé)

Google Maps utilise probablement:
- GTFS-RT via un accord avec Divia/Keolis
- Ou l'API Navitia

MEILLEURE APPROCHE:
Inspectez les requêtes réseau directement dans votre navigateur !
""")

print("\n" + "=" * 80)
