"""
Script pour migrer automatiquement tous les scripts Divia
de l'ancienne API TOTEM vers la nouvelle API GTFS-RT
"""

import os
import re

# Liste des fichiers à migrer (sans les tests et scripts d'analyse)
scripts_to_migrate = [
    "l5-talant-wilsoncarnot.py",
    "l5-talant-transvaal.py",
    "l5-talant-agrosup.py",
    "l5-univ-baudin.py",
    "l6-toison-wilsoncar.py",
    "l8-chicago-baudin.py",
    "l8-saintappo-wilsoncarnot.py",
    "pl-rep-wilsoncarnot.py",
    "pl-univ-baudin.py",
]

def extract_line_and_stop(content):
    """Extrait les IDs de ligne et d'arrêt du contenu du script"""
    line_match = re.search(r'api\.get_line\("(\d+)"\)', content)
    stop_match = re.search(r'stop = line\.get_stop\("(\d+)"\)', content)
    
    if line_match and stop_match:
        return line_match.group(1), stop_match.group(1)
    return None, None

def get_comment_from_original(content):
    """Extrait le commentaire de la ligne pour le garder"""
    line_match = re.search(r'api\.get_line\("(\d+)"\)\s*#\s*(.+)', content)
    if line_match:
        return line_match.group(2)
    return ""

def migrate_script(filepath):
    """Migre un script vers la nouvelle API GTFS-RT"""
    print(f"\nTraitement de {os.path.basename(filepath)}...")
    
    # Lire le contenu original
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extraire les paramètres
    ligne_id, arret_code = extract_line_and_stop(content)
    comment = get_comment_from_original(content)
    
    if not ligne_id or not arret_code:
        print(f"  ⚠ Impossible d'extraire les paramètres, ignoré")
        return False
    
    print(f"  Ligne: {ligne_id} ({comment})")
    print(f"  Arrêt: {arret_code}")
    
    # Déterminer la logique de sortie (999 ou N/A pour erreur)
    uses_999 = '"999"' in content or "'999'" in content
    error_value = '"999"' if uses_999 else '"N/A"'
    
    # Détection du cas spécial "bus à l'arrêt" (minutes_prochain_bus == 1439)
    has_bus_at_stop_check = "1439" in content
    
    # Générer le nouveau contenu
    new_content = f'''#!/usr/bin/env python3
"""
Script pour récupérer les horaires temps réel
Ligne: {comment if comment else ligne_id}
Arrêt: {arret_code}

Utilise la nouvelle API GTFS-RT depuis transport.data.gouv.fr
(l'ancienne API TOTEM ne fonctionne plus depuis la refonte du site Divia)
"""

from divia_api.gtfs_realtime import get_next_buses

# Ligne {ligne_id}{' - ' + comment if comment else ''}, Arrêt {arret_code}
result = get_next_buses("{ligne_id}", "{arret_code}", count=2)

minutes_prochain_bus = result.get('minutes_prochain')
minutes_suivant_bus = result.get('minutes_suivant')
'''
    
    # Ajouter la logique spéciale si elle existait
    if has_bus_at_stop_check:
        new_content += '''
# Gestion du cas où le bus est à l'arrêt (1 minute = bus présent)
if minutes_prochain_bus is not None and minutes_prochain_bus <= 1:
    minutes_prochain_bus = 0
'''
    
    # Logique de fallback en cas d'erreur
    new_content += f'''
# Conversion en format attendu (N/A si pas de données)
if minutes_prochain_bus is None:
    minutes_prochain_bus = {error_value}
if minutes_suivant_bus is None:
    minutes_suivant_bus = {error_value}

print(f'{{{{"prochain_bus": {{minutes_prochain_bus}}, "suivant_bus": {{minutes_suivant_bus}}}}}}')
'''
    
    # Créer une sauvegarde
    backup_path = filepath + ".old"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✓ Sauvegarde créée: {os.path.basename(backup_path)}")
    
    # Écrire le nouveau contenu
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"  ✓ Script migré avec succès")
    
    return True

def main():
    print("=" * 80)
    print("MIGRATION DES SCRIPTS DIVIA VERS GTFS-RT")
    print("=" * 80)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    migrated = 0
    
    for script_name in scripts_to_migrate:
        filepath = os.path.join(script_dir, script_name)
        
        if not os.path.exists(filepath):
            print(f"\n⚠ Fichier non trouvé: {script_name}")
            continue
        
        if migrate_script(filepath):
            migrated += 1
    
    print("\n" + "=" * 80)
    print(f"RÉSUMÉ: {migrated}/{len(scripts_to_migrate)} scripts migrés")
    print("=" * 80)
    print("""
Les fichiers originaux ont été sauvegardés avec l'extension .old
Vous pouvez les supprimer une fois que vous avez vérifié que tout fonctionne.

Pour tester un script migré:
  python <nom_du_script>.py

Pour supprimer les sauvegardes:
  del *.old
""")

if __name__ == "__main__":
    main()
