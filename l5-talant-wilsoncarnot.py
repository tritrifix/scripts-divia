#!/usr/bin/env python3
"""
Script pour récupérer les horaires temps réel
Ligne: L5 talant
Arrêt: 141

Utilise la nouvelle API GTFS-RT depuis transport.data.gouv.fr
(l'ancienne API TOTEM ne fonctionne plus depuis la refonte du site Divia)
"""

from divia_api.gtfs_realtime import get_next_buses

# Ligne 87 - L5 talant, Arrêt 141
result = get_next_buses("87", "141", count=2)

minutes_prochain_bus = result.get('minutes_prochain')
minutes_suivant_bus = result.get('minutes_suivant')

# Gestion du cas où le bus est à l'arrêt (1 minute = bus présent)
if minutes_prochain_bus is not None and minutes_prochain_bus <= 1:
    minutes_prochain_bus = 0

# Conversion en format attendu (N/A si pas de données)
if minutes_prochain_bus is None:
    minutes_prochain_bus = "999"
if minutes_suivant_bus is None:
    minutes_suivant_bus = "999"

print(f'{{"prochain_bus": {minutes_prochain_bus}, "suivant_bus": {minutes_suivant_bus}}}')

