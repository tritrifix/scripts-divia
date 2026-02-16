#!/usr/bin/env python3
"""
Script pour récupérer les horaires temps réel
Ligne: L5 talant
Arrêt: 748

Utilise la nouvelle API GTFS-RT depuis transport.data.gouv.fr
(l'ancienne API TOTEM ne fonctionne plus depuis la refonte du site Divia)
"""

from divia_api.gtfs_realtime import get_next_buses

# Ligne 87 - L5 talant, Arrêt 748
result = get_next_buses("87", "748", count=2)

minutes_prochain_bus = result.get('minutes_prochain')
minutes_suivant_bus = result.get('minutes_suivant')

# Conversion en format attendu (N/A si pas de données)
if minutes_prochain_bus is None:
    minutes_prochain_bus = "N/A"
if minutes_suivant_bus is None:
    minutes_suivant_bus = "N/A"

print(f'{{"prochain_bus": {minutes_prochain_bus}, "suivant_bus": {minutes_suivant_bus}}}')

