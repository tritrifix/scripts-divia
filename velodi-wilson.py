from divia_api import VelodiAPI

velodi_api = VelodiAPI()

#station = velodi_api.find_station("Wilson")  # Récupération de la station DiviaVélodi « Wilson ».

station = velodi_api.get_station("11")  # Récupération d’une station par son identifiant. Ici, l’identifiant « 11 » correspond à la station « Wilson ».

realtime = station.check()  # Requête de données à jour sur la disponibilité des vélos et des emplacements dans cette station.

print(f'{{"bike": {realtime.bikes}, "dock": {realtime.docks}}}')

## test