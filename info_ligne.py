#!/usr/bin/env python3
"""
Script pour afficher toutes les informations d'une ligne de bus Divia.

Usage:
    python info_ligne.py <nom_ligne> [sens]

Exemples:
    python info_ligne.py L5
    python info_ligne.py B12
    python info_ligne.py L5 R        # sens retour
    python info_ligne.py 87          # par ID TOTEM
"""

import sys
from datetime import datetime

from divia_api.api import DiviaAPI
from divia_api.gtfs_realtime import GTFSRealtimeAPI


# ─── Utilitaires ──────────────────────────────────────────────────────────────

def separateur(titre="", car="─", largeur=60):
    if titre:
        print(f"\n{car * 3} {titre} {car * (largeur - len(titre) - 5)}")
    else:
        print(car * largeur)


def afficher_infos_statiques(ligne_data):
    """Affiche les informations statiques de la ligne (arrêts, direction, etc.)."""
    separateur("INFORMATIONS GÉNÉRALES")
    print(f"  Nom         : {ligne_data.get('codetotem', 'N/A')}")
    print(f"  ID interne  : {ligne_data.get('id', 'N/A')}")
    print(f"  Sens        : {ligne_data.get('senstotem', 'N/A')}")
    print(f"  Accessibilité UFR : {ligne_data.get('ufr', 'N/A')}")

    arrets = ligne_data.get("arrets", {})
    separateur(f"ARRÊTS ({len(arrets)})")
    for i, (_, arret) in enumerate(arrets.items(), 1):
        ufr = " ♿" if arret.get("ufr") else ""
        print(f"  {i:>3}. [{arret.get('id', '?'):>5}]  {arret.get('nom', 'Inconnu')}{ufr}")


def afficher_vehicules(ligne_id):
    """Affiche les véhicules en circulation sur la ligne."""
    separateur("VÉHICULES EN CIRCULATION (temps réel)")
    vehicules = GTFSRealtimeAPI.get_vehicle_positions(ligne_id)
    if not vehicules:
        print("  Aucun véhicule détecté sur cette ligne.")
        return

    print(f"  {len(vehicules)} véhicule(s) actif(s) :\n")
    for i, veh in enumerate(vehicules, 1):
        route = veh.get("route_id", "?")
        trip  = veh.get("trip_id", "?")
        lat   = veh.get("latitude")
        lon   = veh.get("longitude")
        speed = veh.get("speed")

        print(f"  Véhicule #{i}")
        print(f"    Route   : {route}")
        print(f"    Trajet  : {trip}")
        if lat is not None and lon is not None:
            print(f"    Position: {lat:.5f}, {lon:.5f}")
            print(f"    Maps    : https://www.google.com/maps?q={lat:.5f},{lon:.5f}")
        if speed is not None:
            print(f"    Vitesse : {speed * 3.6:.1f} km/h")
        print()


def afficher_prochains_departs(ligne_id, arrets, max_arrets=None):
    """Affiche les prochains passages temps réel à chaque arrêt de la ligne."""
    separateur("PROCHAINS PASSAGES (temps réel)")

    items = list(arrets.items())
    if max_arrets:
        items = items[:max_arrets]

    for _, arret in items:
        arret_id = arret.get("id", "")
        arret_nom = arret.get("nom", "Inconnu")
        departures = GTFSRealtimeAPI.get_next_departures(ligne_id, str(arret_id), limit=3)

        if departures:
            passages = ", ".join(
                f"{d['formatted']} ({d['minutes']} min)" for d in departures
            )
            print(f"  {arret_nom:<35} → {passages}")
        # Si pas de données en temps réel on passe silencieusement


# ─── Programme principal ───────────────────────────────────────────────────────

def main():
    # Récupération des arguments
    if len(sys.argv) < 2:
        print("Usage : python info_ligne.py <nom_ligne> [sens (A/R)]")
        print("Exemples :")
        print("  python info_ligne.py L5")
        print("  python info_ligne.py B12 R")
        sys.exit(1)

    nom_ligne = sys.argv[1].upper()
    sens = sys.argv[2].upper() if len(sys.argv) >= 3 else "A"

    print(f"\n{'═' * 60}")
    print(f"  DIVIA — Informations complètes : ligne {nom_ligne}  (sens {sens})")
    print(f"  Heure d'interrogation : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"{'═' * 60}")

    # Connexion à l'API
    print("\n  Connexion à l'API Divia...")
    try:
        api = DiviaAPI()
    except Exception as e:
        print(f"  ❌ Impossible de se connecter à l'API : {e}")
        sys.exit(1)

    # Recherche de la ligne
    ligne = api.find_line(nom_ligne, sens)
    if ligne is None:
        # Tentative sans le sens
        ligne = api.find_line(nom_ligne, "A")
        if ligne is None:
            print(f"  ❌ Ligne '{nom_ligne}' introuvable.")
            print("\n  Lignes disponibles :")
            lignes = api.network.get("arborescence", {}).get("lignes", {})
            codes = sorted(set(v.get("codetotem", "") for v in lignes.values()))
            for c in codes:
                print(f"    - {c}")
            sys.exit(1)

    ligne_data = ligne.line_data
    ligne_id   = ligne_data.get("id", "")

    # 1. Informations statiques
    afficher_infos_statiques(ligne_data)

    # 2. Positions des véhicules (temps réel)
    afficher_vehicules(ligne_id)

    # 3. Prochains passages à chaque arrêt
    arrets = ligne_data.get("arrets", {})
    if arrets:
        print("  (Récupération des passages temps réel — peut prendre quelques secondes…)\n")
        afficher_prochains_departs(ligne_id, arrets)

    separateur(car="═")
    print()


if __name__ == "__main__":
    main()
