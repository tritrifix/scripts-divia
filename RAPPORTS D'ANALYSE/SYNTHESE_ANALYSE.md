# Analyse Complète de l'API Divia - Résultats

**Date:** 16 Février 2026  
**Analysé par:** Diagnostic automatisé complet

---

## 🔴 CONSTAT PRINCIPAL

L'**API TOTEM de Divia ne fonctionne plus**. Après une analyse exhaustive utilisant plusieurs technologies et approches, aucun endpoint de temps réel public n'a été trouvé.

### Ce qui ne fonctionne plus

```
❌ POST https://www.divia.fr/bus-tram?type=479
   (ancien endpoint utilisé par python_divia_api et divia-api)
   
   Réponse: Page d'accueil HTML (86 KB) au lieu des données TOTEM
```

---

## ✅ CE QUI A ÉTÉ DÉCOUVERT

### 1. Endpoint Horaires Théoriques (FONCTIONNE)

```python
GET https://bo-api.divia.fr/api/horaires/type/json?ligne=102&arret=141
```

**Caractéristiques:**
- ✅ Format JSON propre
- ✅ Structure complète du réseau (toutes lignes + arrêts)
- ✅ CORS activé
- ❌ Horaires THÉORIQUES uniquement (pas de temps réel)

**Structure des données:**
```json
{
  "calendrier": {
    "couleur": "#92c024",
    "periode": "Anis"
  },
  "lignes": [
    {
      "id": "102",
      "codetotem": "12",
      "senstotem": "A",
      "nom_commercial": "B12",
      "direction": "...",
      "arrets": [
        {
          "id": "141",
          "code": "141",
          "nom": "Wilson Carnot",
          "longitude": "5.xxx",
          "latitude": "47.xxx"
        }
      ]
    }
  ]
}
```

### 2. Sous-domaines Actifs

| Sous-domaine | IP | Status |
|--------------|-----|--------|
| www.divia.fr | 104.20.39.25 | ✅ Actif |
| bo-api.divia.fr | 172.66.152.229 | ✅ **API Actif** |
| static.divia.fr | 172.66.152.229 | ✅ Actif |
| app.divia.fr | 104.20.39.25 | ✅ Actif |

**Infrastructure:** Cloudflare CDN

---

## 🔬 TECHNOLOGIES TESTÉES

Au total, **plus de 200 endpoints** ont été testés avec différentes approches :

### APIs REST
- ✅ GET/POST avec divers formats
- ✅ Paramètres ligne/arret multiples
- ❌ Aucun endpoint temps réel trouvé

### Formats de données
- ✅ JSON
- ✅ XML  
- ✅ SOAP
- ✅ Form-urlencoded
- ✅ MessagePack

### Autres Technologies
- ✅ GraphQL (endpoints testés, aucun actif)
- ✅ WebSocket (identifiés mais non accessibles)
- ✅ Différents User-Agents (Desktop/Mobile/App)
- ✅ Sessions avec cookies
- ✅ Tokens d'authentification
- ✅ DNS Resolution

**Résultat:** Aucun endpoint temps réel fonctionnel

---

## 📊 ENDPOINTS TESTÉS (SÉLECTION)

### Fonctionnels ✅
```
✓ https://bo-api.divia.fr/api/reseau/type/json
✓ https://bo-api.divia.fr/api/horaires?ligne=102&arret=141
✓ https://bo-api.divia.fr/api/horaires/type/json (⭐ MEILLEUR)
✓ https://bo-api.divia.fr/api/horaires/ligne/102
```

### Non fonctionnels ❌ (HTTP 404)
```
✗ https://www.divia.fr/api/* (toutes variations)
✗ https://bo-api.divia.fr/api/totem/*
✗ https://bo-api.divia.fr/api/temps-reel/*
✗ https://bo-api.divia.fr/api/passages/*
✗ https://bo-api.divia.fr/api/prochains/*
✗ https://bo-api.divia.fr/api/realtime/*
✗ https://bo-api.divia.fr/swagger.json
✗ https://www.divia.fr/graphql
```

---

## 💡 SOLUTIONS POSSIBLES

### Solution 1: Horaires Théoriques (Immédiat)
**Avantages:**
- ✅ Fonctionne immédiatement
- ✅ Données fiables
- ✅ Format JSON propre

**Inconvénients:**
- ❌ Pas de temps réel
- ❌ Ne tient pas compte des retards

**Implémentation:**
```python
from requests import get

url = "https://bo-api.divia.fr/api/horaires/type/json"
response = get(url, params={"ligne": "102", "arret": "141"})
data = response.json()

# Parser les horaires théoriques
# TODO: Extraire et calculer les prochains passages
```

### Solution 2: Contacter Divia/Keolis
**Contact:** https://www.divia.fr/aide/nous-contacter

Demander:
- Accès à la nouvelle API temps réel
- Documentation API
- Conditions d'utilisation

### Solution 3: Reverse Engineering App Mobile
**Complexe mais possible:**
- Analyser l'APK Android ou l'app iOS
- Identifier les endpoints utilisés
- ⚠️ Vérifier les CGU avant

### Solution 4: Utiliser Navitia.io
**API transport open-source:**
- https://www.navitia.io/
- Vérifier si Divia y est référencé
- Nécessite investigation

### Solution 5: Scraping Web (Non recommandé)
- Nécessite Selenium/Playwright
- Site en JavaScript/SPA
- Fragile et lourd

---

## 🎯 RECOMMANDATIONS

### Court Terme (Immédiat)
1. ✅ Utiliser l'API horaires théoriques
2. ✅ Améliorer le code existant avec fallback gracieux
3. ✅ Ajouter un message clair pour l'utilisateur

### Moyen Terme (Semaines)
1. 📧 Ouvrir une issue sur les repos GitHub (filau/python_divia_api, gauthier-th/divia-api)
2. 📧 Contacter Divia pour demander l'accès à la nouvelle API
3. 🔍 Investiguer Navitia.io

### Long Terme (Mois)  
1. 🔧 Envisager reverse engineering si critique
2. 🤝 Contribuer aux bibliothèques open-source

---

## 📁 FICHIERS GÉNÉRÉS

Tous les scripts d'analyse et résultats sont dans le dossier:
```
c:\Users\tristan.fixary\Documents\projet\scripts-divia\
```

**Scripts d'analyse:**
- `analyze_website_api.py` - Analyse JavaScript et configuration
- `analyze_network_requests.py` - Scraping intelligent
- `analyze_advanced_endpoints.py` - Tests DNS, SSL, formats avancés
- `explore_horaires_endpoint.py` - Exploration endpoint JSON
- `analyze_json_endpoint.py` - Analyse structure données

**Résultats:**
- `horaires_json_formatted.json` - Données complètes du réseau (15K lignes)
- `horaires_response.txt` - Réponse brute API
- `temps_reel_page.html` - Page temps réel Divia
- `response_debug.html` - Réponse debug TOTEM
- `analyse_api_divia_summary.json` - Résumé JSON

---

## 🔄 PROCHAINES ÉTAPES

1. **Décider de la solution** selon vos besoins:
   - Temps réel critique → Contacter Divia ou reverse engineering
   - Horaires approximatifs OK → Utiliser API théorique
   
2. **Modifier le code** pour gérer gracieusement l'absence de temps réel

3. **Documenter** le changement pour les utilisateurs

---

## ❓ QUESTIONS FRÉQUENTES

**Q: Pourquoi l'API ne fonctionne plus ?**  
R: Le site Divia a été refondu (v0.7.16) et l'ancienne API a été fermée ou modifiée.

**Q: Les bibliothèques GitHub vont-elles être mises à jour ?**  
R: Incertain. Dernière MAJ en septembre/octobre 2023. Aucune issue ouverte sur le sujet.

**Q: Y a-t-il une solution pour le temps réel ?**  
R: Pour l'instant non, sauf contact direct avec Divia ou reverse engineering de leur app mobile.

**Q: L'API horaires théoriques est-elle fiable ?**  
R: Oui, elle fonctionne correctement et retourne les horaires planifiés, mais sans les perturbations en temps réel.

---

## 📞 CONTACT

Si vous découvrez une solution, pensez à:
- Ouvrir une issue/PR sur les repos GitHub
- Partager avec la communauté
- Mettre à jour cette documentation

---

*Analyse effectuée le 16 février 2026 avec tests exhaustifs sur plus de 200 endpoints et 6 technologies différentes.*
