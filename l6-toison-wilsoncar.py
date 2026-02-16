from divia_api import DiviaAPI
import datetime

api = DiviaAPI()
line = api.get_line("90")  # L6 toison
stop = line.get_stop("141")  # Wilson Carnot
totem_result = stop.totem()  # Interrogation du service TOTEM et récupération des prochains horaires. C’est une liste d’objets « datetime.datetime » qui est retournée par la fonction.

if len(totem_result) >= 2:
    now = datetime.datetime.now()
    prochain_bus = totem_result[0]
    suivant_bus = totem_result[1]
    minutes_prochain_bus = max(0, (prochain_bus - now).seconds // 60)
    minutes_suivant_bus = max(0, (suivant_bus - now).seconds // 60)
else:
    minutes_prochain_bus = "N/A"
    minutes_suivant_bus = "N/A"

print(f'{{"prochain_bus": {minutes_prochain_bus}, "suivant_bus": {minutes_suivant_bus}}}')