#!/usr/bin/env python3
"""
Script pour trouver rapidement les IDs GTFS (route_id et stop_id)
d'une ligne et/ou d'un arrêt Divia.

Usage:
    python find_ids.py <ligne> <arret>
    python find_ids.py <ligne>
    python find_ids.py <arret>

Exemples:
    python find_ids.py L5 Baudin
    python find_ids.py B12 "Wilson Carnot"
    python find_ids.py L5
    python find_ids.py Baudin
"""

import sys
from divia_api.api import DiviaAPI
from divia_api.normalize_characters import normalize
from divia_api.gtfs_realtime import GTFSRealtimeAPI


def chercher_ligne(api, recherche):
    """Retourne toutes les lignes correspondant au nom."""
    lignes = api.network.get("arborescence", {}).get("lignes", {})
    resultats = []
    for _, l in lignes.items():
        if normalize(l.get("codetotem", "").lower()) == normalize(recherche.lower()):
            resultats.append(l)
    return resultats


def chercher_arret_global(api, recherche):
    """Retourne tous les arrêts correspondant (dans toutes les lignes)."""
    lignes = api.network.get("arborescence", {}).get("lignes", {})
    resultats = {}  # stop_id → {nom, lignes[]}
    recherche_norm = normalize(recherche.lower())
    for _, ligne_data in lignes.items():
        for _, arret in ligne_data.get("arrets", {}).items():
            arret_nom = arret.get("nom", "")
            arret_id  = str(arret.get("id", ""))
            match_id  = (arret_id == recherche)
            match_nom = recherche_norm in normalize(arret_nom.lower())
            if match_id or match_nom:
                if arret_id not in resultats:
                    resultats[arret_id] = {"nom": arret_nom, "lignes": []}
                resultats[arret_id]["lignes"].append({
                    "ligne_id":  ligne_data.get("id", ""),
                    "ligne_nom": ligne_data.get("codetotem", ""),
                    "sens":      ligne_data.get("senstotem", "A"),
                })
    return resultats


def gtfs_route_id(ligne_id):
    return GTFSRealtimeAPI._get_route_id(ligne_id)


def gtfs_stop_id(stop_id):
    return GTFSRealtimeAPI._get_stop_id(stop_id)


def afficher_resultats_ligne(lignes_data, filtre_arret=None, arrets_data=None):
    noms_vus = set()
    for l in lignes_data:
        nom = l.get("codetotem", "")
        sens = l.get("senstotem", "A")
        lid  = l.get("id", "")
        cle  = (nom, sens)

        if cle in noms_vus:
            continue
        noms_vus.add(cle)

        sens_label = "Aller" if sens == "A" else "Retour"
        route_gtfs = gtfs_route_id(lid)
        print(f"  Ligne    : {nom}  ({sens_label})")
        print(f"  ligne_id : {lid}")
        print(f"  route_id : {route_gtfs}")

        if filtre_arret and arrets_data:
            # Chercher l'arrêt dans cette ligne spécifique
            arrets = l.get("arrets", {})
            filtre_norm = normalize(filtre_arret.lower())
            for _, arret in arrets.items():
                arret_nom = arret.get("nom", "")
                arret_id  = str(arret.get("id", ""))
                if filtre_norm in normalize(arret_nom.lower()) or arret_id == filtre_arret:
                    stop_gtfs = gtfs_stop_id(arret_id)
                    print(f"  Arrêt    : {arret_nom}")
                    print(f"  stop_id  : {stop_gtfs}  (arret_id={arret_id})")

        print()


def main():
    if len(sys.argv) < 2:
        print("Usage : python find_ids.py <ligne> [arret]")
        print("        python find_ids.py <arret>")
        print()
        print("Exemples :")
        print('  python find_ids.py L5 Baudin')
        print('  python find_ids.py B12 "Wilson Carnot"')
        print('  python find_ids.py L5')
        print('  python find_ids.py Baudin')
        sys.exit(1)

    print("\n  Connexion à l'API Divia…")
    try:
        api = DiviaAPI()
    except Exception as e:
        print(f"  ❌ Erreur : {e}")
        sys.exit(1)

    args    = sys.argv[1:]
    arg1    = args[0]
    arg2    = args[1] if len(args) >= 2 else None

    # Chercher en tant que ligne
    lignes_trouvees = chercher_ligne(api, arg1)

    if lignes_trouvees:
        # arg1 = ligne, arg2 = arrêt (optionnel)
        print(f"\n{'─'*50}")
        print(f"  Résultats GTFS pour : ligne={arg1}" + (f", arrêt={arg2}" if arg2 else ""))
        print(f"{'─'*50}\n")
        afficher_resultats_ligne(lignes_trouvees, filtre_arret=arg2, arrets_data=True)

        # Afficher les stop_ids de l'arrêt si précisé
        if arg2:
            arrets = chercher_arret_global(api, arg2)
            if arrets:
                print(f"{'─'*50}")
                print(f"  Tous les stop_id GTFS pour l'arrêt « {arg2} » :\n")
                for stop_id, info in sorted(arrets.items()):
                    lignes_str = ", ".join(sorted(set(l["ligne_nom"] for l in info["lignes"])))
                    print(f"  {info['nom']:<35}  stop_id={gtfs_stop_id(stop_id):<12}  (id={stop_id})  Lignes: {lignes_str}")
                print()

    else:
        # arg1 = peut-être un arrêt
        arrets = chercher_arret_global(api, arg1)
        if arrets:
            print(f"\n{'─'*50}")
            print(f"  Résultats GTFS pour l'arrêt « {arg1} » :\n")
            for stop_id, info in sorted(arrets.items()):
                lignes_str = ", ".join(sorted(set(
                    f"{l['ligne_nom']} ({'A' if l['sens']=='A' else 'R'})" for l in info["lignes"]
                )))
                print(f"  Arrêt    : {info['nom']}")
                print(f"  stop_id  : {gtfs_stop_id(stop_id):<12}  (id={stop_id})")
                print(f"  Lignes   : {lignes_str}")
                print()
        else:
            print(f"\n  ❌ Aucun résultat pour « {arg1} »")
            if arg2:
                print(f"  ❌ Aucun résultat pour « {arg2} »")
            sys.exit(1)


if __name__ == "__main__":
    main()
