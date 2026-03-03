"""
Script pour corriger la syntaxe f-string dans tous les scripts de lignes
"""

import os
import re

# Scripts à corriger
scripts = [
    "l5-talant-transvaal.py",
    "l5-talant-agrosup.py",
    "l5-univ-baudin.py",
    "l6-toison-wilsoncar.py",
    "l8-chicago-baudin.py",
    "l8-saintappo-wilsoncarnot.py",
    "pl-rep-wilsoncarnot.py",
    "pl-univ-baudin.py",
]

for script_name in scripts:
    if not os.path.exists(script_name):
        print(f"⚠ {script_name} non trouvé")
        continue
    
    with open(script_name, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remplacer la mauvaise syntaxe par la bonne
    # Chercher: print(f'{"prochain_bus": {minutes_prochain_bus}, "suivant_bus": {minutes_suivant_bus}}')
    # Remplacer par: print(f'{{"prochain_bus": {minutes_prochain_bus}, "suivant_bus": {minutes_suivant_bus}}}')
    
    old_pattern = r"print\(f'\{\"prochain_bus\": \{minutes_prochain_bus\}, \"suivant_bus\": \{minutes_suivant_bus\}\}'\)"
    new_string = r"print(f'{" + r'{"prochain_bus": {minutes_prochain_bus}, "suivant_bus": {minutes_suivant_bus}}' + r"}')"
    
    # Approche simple: chercher toutes les variantes possibles
    patterns = [
        (r"print\(f'\{\"prochain_bus\":", r"print(f'{" + r'{"prochain_bus":'),
        (r", \"suivant_bus\": \{minutes_suivant_bus\}\}'\)", r', "suivant_bus": {minutes_suivant_bus}}' + r"}')"),
        # Cas avec guillemets simples mal échappés
        (r"print\(f'\{\{\"prochain_bus\":", r"print(f'{" + r'{"prochain_bus":'),
        (r"suivant_bus\}\}''", "}}'"),
    ]
    
    # Plus simple: remplacer directement la ligne complète
    if 'print(f\'{"prochain_bus":' in content or "print(f'{{\"prochain_bus\":" in content:
        # Trouver et remplacer toute la ligne
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'print(f' in line and 'prochain_bus' in line:
                lines[i] = 'print(f\'{{"prochain_bus": {minutes_prochain_bus}, "suivant_bus": {minutes_suivant_bus}}}\')'
        content = '\n'.join(lines)
        
        with open(script_name, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ {script_name} corrigé")
    else:
        print(f"- {script_name} déjà OK")

print("\nTest d'un script:")
import subprocess
result = subprocess.run(['python', 'l6-toison-wilsoncar.py'], capture_output=True, text=True)
print(f"L6: {result.stdout.strip()}")
