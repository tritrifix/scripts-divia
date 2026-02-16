from divia_api import VelodiAPI

velodi_api = VelodiAPI()

#station = velodi_api.find_station("Auxonne - Eldorado")  # Récupération de la station DiviaVélodi « Auxonne - Eldorado ».

station = velodi_api.get_station("37")  # Récupération d’une station par son identifiant. Ici, l’identifiant « 37 » correspond à la station « Auxonne - Eldorado ».

realtime = station.check()  # Requête de données à jour sur la disponibilité des vélos et des emplacements dans cette station.

print(f'{{"bike": {realtime.bikes}, "dock": {realtime.docks}}}')