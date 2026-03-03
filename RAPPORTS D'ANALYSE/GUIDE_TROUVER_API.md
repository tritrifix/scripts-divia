# 🔍 GUIDE: Comment Trouver l'API Temps Réel de Divia

## 📋 Ce que vous m'avez confirmé

Vous pouvez voir les horaires en temps réel sur:
- ✅ https://www.divia.fr/se-deplacer/temps-reel (fonctionne)
- ✅ Google Maps (a les données temps réel)

**Conclusion:** L'API temps réel existe et fonctionne, mais utilise un nouveau format !

---

## 🎯 MÉTHODE 1: Inspecter les Requêtes Réseau (RECOMMANDÉ)

### Étapes à suivre:

#### 1. Ouvrir Chrome/Firefox DevTools

1. Ouvrez Chrome ou Firefox
2. Allez sur: https://www.divia.fr/se-deplacer/temps-reel
3. Appuyez sur **F12** (ou clic droit → "Inspecter")
4. Cliquez sur l'onglet **"Network"** (Réseau)

#### 2. Filtrer les requêtes

1. Dans l'onglet Network, cliquez sur **"XHR"** ou **"Fetch/XHR"**
2. Cochez **"Preserve log"** (Conserver le journal)
3. Cliquez sur l'icône 🗑️ (Clear) pour vider les requêtes existantes

#### 3. Déclencher la requête temps réel

1. Sur la page Divia, **sélectionnez votre ligne** (ex: B12)
2. **Sélectionnez votre arrêt** (ex: Wilson Carnot)
3. **Observez les nouvelles requêtes** qui apparaissent dans l'onglet Network

#### 4. Identifier l'API

Cherchez une requête qui ressemble à:
- Une URL contenant: `api`, `temps-reel`, `prochains-passages`, `totem`, etc.
- Type: XHR ou Fetch
- Status: 200

#### 5. Copier les détails

Quand vous trouvez la bonne requête:

1. **Clic droit** sur la requête
2. **"Copy as cURL"** ou **"Copy → Copy as fetch"**
3. Collez-moi le résultat ici !

**OU**

Notez manuellement:
- **URL complète** (ex: https://www.divia.fr/api/...)
- **Méthode** (GET ou POST)
- **Onglet "Headers"** → Voir les "Request Headers"
- **Onglet "Payload"** → Voir les paramètres envoyés (si POST)
- **Onglet "Response"** → Voir les données reçues

---

## 🎯 MÉTHODE 2: Utiliser mon script de test

Exécutez ce test pour voir si Navitia ou GTFS-RT est disponible:

```bash
python test_gtfs_navitia.py
```

---

## 🎯 MÉTHODE 3: Tester Navitia.io

Divia utilise le système Navitia (détecté dans les URLs de l'API).

### Étapes:

1. **Créer un compte gratuit**:
   - Allez sur: https://www.navitia.io/
   - Créez un compte
   - Obtenez votre **clé API** (token)

2. **Tester l'API**:
   ```bash
   curl -H "Authorization: YOUR_API_KEY" \
     "https://api.navitia.io/v1/coverage/fr-bfc/networks/network:CGD/lines"
   ```

3. **Documentation**:
   - https://doc.navitia.io/
   - Cherchez "Dijon" ou "Divia" dans la coverage

---

## 📝 Ce dont j'ai besoin de vous

Pour que je puisse corriger les scripts, j'ai besoin que vous me donniez:

### Informations critiques:

1. **L'URL exacte** de l'API temps réel (trouvée via DevTools)
   - Exemple: `https://www.divia.fr/api/v2/prochains-passages`

2. **La méthode** HTTP
   - GET ou POST ?

3. **Les paramètres**
   - Si GET: Les query parameters (`?ligne=102&arret=141`)
   - Si POST: Le body (JSON ou form-data)

4. **Les headers** requis (s'il y en a)
   - Authorization ?
   - Content-Type ?
   - X-API-Key ?

5. **Un exemple de réponse**
   - Quelques lignes du JSON retourné

---

## 📸 Captures d'écran

Si vous préférez, vous pouvez aussi:
1. Faire une capture d'écran de l'onglet Network avec la requête
2. Faire une capture du "Response" (la réponse JSON)
3. Me les envoyer

---

## 🚀 Une fois que j'aurai ces infos

Je pourrai:
1. ✅ Corriger immédiatement la bibliothèque `divia_api`
2. ✅ Mettre à jour tous vos scripts
3. ✅ Créer une nouvelle version fonctionnelle
4. ✅ Ouvrir une PR sur les repos GitHub pour aider la communauté

---

## ❓ Questions Fréquentes

**Q: Pourquoi ne pouvez-vous pas le faire vous-même ?**
R: Le site utilise du JavaScript moderne qui s'exécute dans le navigateur. Les requêtes sont faites dynamiquement après le chargement de la page, donc je ne peux pas les voir en analysant simplement le HTML. Il faut un vrai navigateur.

**Q: C'est compliqué ?**
R: Non ! Ça prend 2 minutes avec DevTools. C'est comme ouvrir le capot pour voir comment le moteur fonctionne.

**Q: Y a-t-il d'autres alternatives ?**
R: Oui, Navitia.io semble être utilisé par Divia et offre une API gratuite. À tester !

---

## 📞 Prochaines Étapes

1. **Option A** (Rapide): Utilisez DevTools et donnez-moi l'URL + paramètres
2. **Option B** (Alternative): Testez Navitia.io avec une clé API
3. **Option C** (Contourner): Utiliser l'API horaires théoriques (moins précis)

Quelle option préférez-vous ?
