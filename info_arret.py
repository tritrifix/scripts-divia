#!/usr/bin/env python3
"""
Script pour afficher toutes les informations d'un arrêt de bus Divia.

Usage:
    python info_arret.py <nom_arret>
    python info_arret.py <id_arret>

Exemples:
    python info_arret.py "Wilson Carnot"
    python info_arret.py 141
    python info_arret.py "Gare SNCF"
"""

import sys
from datetime import datetime

from divia_api.api import DiviaAPI
from divia_api.normalize_characters import normalize
from divia_api.gtfs_realtime import GTFSRealtimeAPI


# ─── Utilitaires ──────────────────────────────────────────────────────────────

def separateur(titre="", car="─", largeur=60):
    if titre:
        print(f"\n{car * 3} {titre} {car * (largeur - len(titre) - 5)}")
    else:
        print(car * largeur)


def chercher_arret(api, recherche):
    """
    Cherche un arrêt dans toutes les lignes.
    Retourne une liste de dict :
      { 'arret_id', 'arret_nom', 'ufr', 'ligne_id', 'ligne_nom', 'sens' }
    """
    resultats = []
    recherche_norm = normalize(recherche.lower())

    lignes = api.network.get("arborescence", {}).get("lignes", {})

    for _, ligne_data in lignes.items():
        for _, arret in ligne_data.get("arrets", {}).items():
            arret_id  = str(arret.get("id", ""))
            arret_nom = arret.get("nom", "")

            # Correspondance par ID ou par nom (normalisé)
            match_id  = (arret_id == recherche)
            match_nom = (normalize(arret_nom.lower()) == recherche_norm)
            # Correspondance partielle si pas de résultat exact
            match_partiel = recherche_norm in normalize(arret_nom.lower())

            if match_id or match_nom or match_partiel:
                resultats.append({
                    "arret_id":  arret_id,
                    "arret_nom": arret_nom,
                    "ufr":       arret.get("ufr", False),
                    "ligne_id":  ligne_data.get("id", ""),
                    "ligne_nom": ligne_data.get("codetotem", ""),
                    "sens":      ligne_data.get("senstotem", "A"),
                })

    return resultats


def regrouper_par_arret(resultats):
    """
    Regroupe les résultats par (arret_id, arret_nom).
    Retourne un dict : { (id, nom) : [lignes...] }
    """
    groupes = {}
    for r in resultats:
        cle = (r["arret_id"], r["arret_nom"])
        groupes.setdefault(cle, []).append({
            "ligne_id":  r["ligne_id"],
            "ligne_nom": r["ligne_nom"],
            "sens":      r["sens"],
            "ufr":       r["ufr"],
        })
    return groupes


def afficher_arret(arret_id, arret_nom, lignes):
    """Affiche toutes les infos d'un arrêt donné."""

    ufr = lignes[0].get("ufr", False)
    accessibilite = "Oui ♿" if ufr else "Non"

    separateur("INFORMATIONS GÉNÉRALES")
    print(f"  Nom de l'arrêt    : {arret_nom}")
    print(f"  ID                : {arret_id}")
    print(f"  Accessibilité UFR : {accessibilite}")

    # Lignes desservant cet arrêt
    separateur(f"LIGNES DESSERVANT CET ARRÊT ({len(lignes)})")
    noms_affiches = set()
    for l in sorted(lignes, key=lambda x: (x["ligne_nom"], x["sens"])):
        cle = (l["ligne_nom"], l["sens"])
        if cle not in noms_affiches:
            noms_affiches.add(cle)
            sens_label = "Aller" if l["sens"] == "A" else "Retour"
            print(f"  [{l['ligne_id']:>5}]  {l['ligne_nom']:<10}  ({sens_label})")

    # Prochains passages par ligne
    separateur("PROCHAINS PASSAGES (temps réel)")
    print("  (Récupération en cours…)\n")

    trouves = 0
    noms_affiches2 = set()
    for l in sorted(lignes, key=lambda x: (x["ligne_nom"], x["sens"])):
        cle = (l["ligne_nom"], l["sens"])
        if cle in noms_affiches2:
            continue
        noms_affiches2.add(cle)

        sens_label = "→" if l["sens"] == "A" else "←"
        departures = GTFSRealtimeAPI.get_next_departures(
            l["ligne_id"], arret_id, limit=3
        )
        if departures:
            trouves += 1
            passages = "  |  ".join(
                f"{d['formatted']} ({d['minutes']} min)" for d in departures
            )
            print(f"  {sens_label} {l['ligne_nom']:<10}  {passages}")
        else:
            print(f"  {sens_label} {l['ligne_nom']:<10}  Aucun passage imminent")

    if trouves == 0:
        print("  Aucune donnée temps réel disponible pour cet arrêt.")


# ─── Programme principal ───────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage : python info_arret.py <nom_ou_id_arret>")
        print("Exemples :")
        print('  python info_arret.py "Wilson Carnot"')
        print("  python info_arret.py 141")
        sys.exit(1)

    recherche = " ".join(sys.argv[1:])

    print(f"\n{'═' * 60}")
    print(f"  DIVIA — Informations arrêt : {recherche}")
    print(f"  Heure d'interrogation : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"{'═' * 60}")

    print("\n  Connexion à l'API Divia…")
    try:
        api = DiviaAPI()
    except Exception as e:
        print(f"  ❌ Impossible de se connecter à l'API : {e}")
        sys.exit(1)

    resultats = chercher_arret(api, recherche)

    if not resultats:
        print(f"\n  ❌ Arrêt '{recherche}' introuvable.")
        sys.exit(1)

    groupes = regrouper_par_arret(resultats)

    # Si plusieurs arrêts distincts correspondent (recherche partielle)
    if len(groupes) > 1:
        print(f"\n  Plusieurs arrêts correspondent à '{recherche}' :\n")
        for (aid, anom), lignes in sorted(groupes.items()):
            noms_lignes = ", ".join(sorted(set(l["ligne_nom"] for l in lignes)))
            print(f"  [{aid:>5}]  {anom:<35}  Lignes : {noms_lignes}")
        print("\n  → Relancez avec le nom exact ou l'ID pour voir le détail.")
        separateur(car="═")
        print()
        sys.exit(0)

    # Arrêt unique : affichage complet
    (arret_id, arret_nom), lignes = next(iter(groupes.items()))
    afficher_arret(arret_id, arret_nom, lignes)

    separateur(car="═")
    print()


if __name__ == "__main__":
    main()
