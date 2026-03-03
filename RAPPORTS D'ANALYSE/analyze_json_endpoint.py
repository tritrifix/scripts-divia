"""
Analyse de l'endpoint JSON découvert: /api/horaires/type/json
"""
from requests import get
import json
from datetime import datetime

print("=" * 80)
print("ANALYSE DE L'ENDPOINT JSON /api/horaires/type/json")
print("=" * 80)

url = "https://bo-api.divia.fr/api/horaires/type/json"
params = {"ligne": "102", "arret": "141"}

print(f"\nRécupération des données...")
response = get(url, params=params, timeout=15)

print(f"Status: {response.status_code}")
print(f"Content-Type: {response.headers.get('Content-Type')}")
print(f"Size: {len(response.content)} bytes")

# Parser le JSON
data = response.json()

print(f"\n{'='*80}")
print(f"STRUCTURE DES DONNÉES")
print(f"{'='*80}\n")

print(f"Clés principales: {list(data.keys())}\n")

# Analyser chaque clé
for key in data.keys():
    value = data[key]
    print(f"[{key}]")
    print(f"  Type: {type(value).__name__}")
    
    if isinstance(value, dict):
        print(f"  Keys: {list(value.keys())}")
        for k, v in list(value.items())[:3]:
            print(f"    {k}: {str(v)[:100]}")
    elif isinstance(value, list):
        print(f"  Length: {len(value)}")
        if len(value) > 0:
            print(f"  First item type: {type(value[0]).__name__}")
            if isinstance(value[0], dict):
                print(f"  First item keys: {list(value[0].keys())}")
    else:
        print(f"  Value: {str(value)[:100]}")
    print()

# Sauvegarder le JSON formaté
with open("horaires_json_formatted.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print("→ JSON sauvegardé dans horaires_json_formatted.json")

# Explorer les lignes
if "lignes" in data:
    print(f"\n{'='*80}")
    print(f"ANALYSE DE LA CLÉ 'lignes'")
    print(f"{'='*80}\n")
    
    lignes = data["lignes"]
    print(f"Type: {type(lignes).__name__}")
    
    if isinstance(lignes, dict):
        print(f"Nombre de lignes: {len(lignes)}")
        print(f"Clés: {list(lignes.keys())[:10]}")
        
        # Prendre la première ligne pour analyse
        for ligne_id, ligne_data in list(lignes.items())[:1]:
            print(f"\nAnalyse de la ligne {ligne_id}:")
            print(f"  Type: {type(ligne_data).__name__}")
            if isinstance(ligne_data, dict):
                print(f"  Keys: {list(ligne_data.keys())}")
                
                for k, v in ligne_data.items():
                    if isinstance(v, (dict, list)):
                        print(f"  {k}: {type(v).__name__} (len={len(v) if isinstance(v, (list, dict)) else 'N/A'})")
                    else:
                        print(f"  {k}: {str(v)[:100]}")

# Chercher des horaires temps réel
print(f"\n{'='*80}")
print(f"RECHERCHE D'HORAIRES TEMPS RÉEL")
print(f"{'='*80}\n")

def search_realtime_data(obj, path="", depth=0):
    """Recherche récursive de données temps réel"""
    if depth > 10:
        return
    
    realtime_keywords = ['temps', 'real', 'totem', 'prochain', 'passage', 'next', 'departure', 'arrival']
    
    if isinstance(obj, dict):
        for key, value in obj.items():
            key_lower = str(key).lower()
            if any(kw in key_lower for kw in realtime_keywords):
                print(f"  Trouvé: {path}.{key}")
                print(f"    Type: {type(value).__name__}")
                if isinstance(value, (str, int, float, bool)):
                    print(f"    Value: {value}")
                elif isinstance(value, (list, dict)):
                    print(f"    Size: {len(value)}")
                print()
            
            search_realtime_data(value, f"{path}.{key}", depth + 1)
    
    elif isinstance(obj, list) and len(obj) > 0:
        search_realtime_data(obj[0], f"{path}[0]", depth + 1)

print("Recherche de clés liées au temps réel...")
search_realtime_data(data)

# Chercher des timestamps / dates récentes
print(f"\n{'='*80}")
print(f"RECHERCHE DE TIMESTAMPS")
print(f"{'='*80}\n")

def search_timestamps(obj, path="", depth=0):
    """Recherche de timestamps ou dates"""
    if depth > 10:
        return
    
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, (int, float)):
                # Vérifier si c'est un timestamp Unix
                try:
                    if 1600000000 < value < 2000000000:  # Range valide pour 2020-2033
                        dt = datetime.fromtimestamp(value)
                        print(f"  Timestamp trouvé: {path}.{key} = {dt}")
                except:
                    pass
            elif isinstance(value, str):
                # Vérifier si c'est une date ISO
                if 'T' in str(value) or '-' in str(value):
                    try:
                        # Tentative de parse
                        if '2026' in str(value) or '2025' in str(value) or '2024' in str(value):
                            print(f"  Date trouvée: {path}.{key} = {value}")
                    except:
                        pass
            
            if isinstance(value, (dict, list)):
                search_timestamps(value, f"{path}.{key}", depth + 1)
    
    elif isinstance(obj, list) and len(obj) > 0:
        search_timestamps(obj[0], f"{path}[0]", depth + 1)

print("Recherche de timestamps...")
search_timestamps(data)

# Test avec la date/heure actuelle
print(f"\n{'='*80}")
print(f"TEST AVEC PARAMÈTRES DATE/HEURE")
print(f"{'='*80}\n")

now = datetime.now()
test_params = [
    {"ligne": "102", "arret": "141", "date": now.strftime("%Y-%m-%d")},
    {"ligne": "102", "arret": "141", "heure": now.strftime("%H:%M")},
    {"ligne": "102", "arret": "141", "timestamp": str(int(now.timestamp()))},
    {"ligne": "102", "arret": "141", "realtime": "1"},
    {"ligne": "102", "arret": "141", "totem": "1"},
]

for params_test in test_params:
    try:
        response = get(url, params=params_test, timeout=5)
        if response.status_code == 200:
            data_test = response.json()
            # Comparer la taille
            size_diff = len(str(data_test)) - len(str(data))
            if abs(size_diff) > 100:  # Si différence significative
                print(f"Params: {params_test}")
                print(f"  → RÉPONSE DIFFÉRENTE! Diff: {size_diff} chars")
                print(f"  → Keys: {list(data_test.keys())}")
    except Exception as e:
        pass

print(f"\n{'='*80}")
print("FIN DE L'ANALYSE")
print(f"{'='*80}")
