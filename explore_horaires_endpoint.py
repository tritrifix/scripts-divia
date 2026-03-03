"""
Exploration approfondie de l'endpoint /api/horaires qui fonctionne
"""
from requests import get
import re
import json

print("=" * 80)
print("EXPLORATION DE L'ENDPOINT /api/horaires")
print("=" * 80)

# Test de l'endpoint horaires
url = "https://bo-api.divia.fr/api/horaires"
params = {"ligne": "102", "arret": "141"}

print(f"\n[1] REQUÊTE DE BASE\n")
print(f"URL: {url}")
print(f"Params: {params}")

response = get(url, params=params, timeout=10)
print(f"Status: {response.status_code}")
print(f"Content-Type: {response.headers.get('Content-Type')}")
print(f"Content-Length: {len(response.content)}")

# Sauvegarder la réponse
with open("horaires_response.txt", "w", encoding="utf-8") as f:
    f.write(response.text)
print("→ Réponse sauvegardée dans horaires_response.txt")

print(f"\n[2] ANALYSE DU CONTENU\n")

# C'est du PHP serialized output (Array), essayons de parser
text = response.text
print("Contenu brut (500 premiers caractères):")
print(text[:500])

# Chercher des patterns intéressants
print(f"\n[3] RECHERCHE DE PATTERNS\n")

# URLs trouvées
urls = re.findall(r'https?://[^\s\)]+', text)
if urls:
    print(f"URLs trouvées ({len(urls)}):")
    for url in urls[:10]:
        print(f"  - {url}")

# Chercher des horaires (format HH:MM)
times = re.findall(r'\b([0-2]?\d):([0-5]\d)\b', text)
if times:
    print(f"\nHoraires trouvés ({len(times)}):")
    for h, m in times[:20]:
        print(f"  - {h}:{m}")

# Chercher des jours/dates
dates = re.findall(r'\b\d{4}-\d{2}-\d{2}\b', text)
if dates:
    print(f"\nDates trouvées: {dates[:10]}")

print(f"\n[4] TEST AVEC DIFFÉRENTS PARAMÈTRES\n")

# Tester différentes variations
test_params = [
    {"ligne": "102", "arret": "141"},
    {"ligne": "102", "arret": "141", "date": "2026-02-16"},
    {"ligne": "102", "arret": "141", "heure": "16:00"},
    {"id_ligne": "102", "id_arret": "141"},
    {"ligne_id": "102", "arret_code": "141"},
]

for params_test in test_params:
    try:
        response = get(url, params=params_test, timeout=5)
        if response.status_code == 200:
            print(f"Params: {params_test}")
            print(f"  → Content length: {len(response.content)}")
            # Vérifier si c'est différent
            if len(response.content) != len(response.content):
                print(f"  → RÉPONSE DIFFÉRENTE!")
    except Exception as e:
        print(f"Params: {params_test} - Error: {type(e).__name__}")

print(f"\n[5] TEST D'AUTRES ENDPOINTS SIMILAIRES\n")

similar_endpoints = [
    ("Passages", "https://bo-api.divia.fr/api/passages", {"ligne": "102", "arret": "141"}),
    ("Temps réel", "https://bo-api.divia.fr/api/temps-reel", {"ligne": "102", "arret": "141"}),
    ("Totem", "https://bo-api.divia.fr/api/totem", {"ligne": "102", "arret": "141"}),
    ("Prochains", "https://bo-api.divia.fr/api/prochains", {"ligne": "102", "arret": "141"}),
    ("Horaires type=json", "https://bo-api.divia.fr/api/horaires/type/json", {"ligne": "102", "arret": "141"}),
    ("Horaires format", "https://bo-api.divia.fr/api/horaires", {"ligne": "102", "arret": "141", "format": "json"}),
]

for name, endpoint, params in similar_endpoints:
    try:
        response = get(endpoint, params=params, timeout=5)
        print(f"{name}: {endpoint}")
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  ✓ Fonctionne!")
            print(f"  Content-Type: {response.headers.get('Content-Type')}")
            print(f"  Length: {len(response.content)}")
            
            # Vérifier si c'est du JSON
            try:
                data = response.json()
                print(f"  ✓✓ JSON valide!")
                print(f"  Keys: {list(data.keys()) if isinstance(data, dict) else 'Array'}")
            except:
                print(f"  Preview: {response.text[:200]}")
    except Exception as e:
        print(f"{name}: {type(e).__name__}")

print(f"\n[6] TEST DES ENDPOINTS AVEC LIGNE SEULEMENT\n")

# Peut-être qu'on peut obtenir tous les arrêts d'une ligne
endpoints_ligne = [
    ("Horaires/ligne", "https://bo-api.divia.fr/api/horaires/ligne/102"),
    ("Ligne/arrets", "https://bo-api.divia.fr/api/ligne/102/arrets"),
    ("Ligne/102", "https://bo-api.divia.fr/api/ligne/102"),
    ("Lignes/102", "https://bo-api.divia.fr/api/lignes/102"),
]

for name, endpoint in endpoints_ligne:
    try:
        response = get(endpoint, timeout=5)
        if response.status_code == 200:
            print(f"{name}: {endpoint}")
            print(f"  ✓ Fonctionne! Length: {len(response.content)}")
    except Exception as e:
        pass

print(f"\n[7] RECHERCHE DANS LA PAGE HTML POUR API JS\n")

# Retourner à la page temps réel pour chercher le JavaScript qui fait les appels
try:
    response = get("https://www.divia.fr/se-deplacer/temps-reel", timeout=15)
    html = response.text
    
    # Chercher des fetch() ou XMLHttpRequest
    fetch_patterns = [
        r'fetch\(["\']([^"\']+)["\']',
        r'\.get\(["\']([^"\']+)["\']',
        r'\.post\(["\']([^"\']+)["\']',
        r'ajax\(["\']([^"\']+)["\']',
        r'url:\s*["\']([^"\']+)["\']',
    ]
    
    api_calls = set()
    for pattern in fetch_patterns:
        matches = re.findall(pattern, html, re.IGNORECASE)
        api_calls.update(matches)
    
    if api_calls:
        print("Appels API trouvés dans le JavaScript:")
        for call in sorted(api_calls):
            if '/api/' in call or 'http' in call:
                print(f"  - {call}")

except Exception as e:
    print(f"Erreur: {e}")

print("\n" + "=" * 80)
print("FIN DE L'EXPLORATION")
print("=" * 80)
