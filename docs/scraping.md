# Documentation Scraping & Sources — SmartPanier

**Auteur :** Armel Houénou — Projet PI HICA 2025-2026  
**Dernière mise à jour :** Juin 2026

---

## 1. Choix des sources

### Sites ciblés

| Site | URL | Type |
|------|-----|------|
| **MyMarket** | mymarket.ma | E-commerce Shopify (HTML statique) |
| **MarketPro** | marketpro.ma | E-commerce WooCommerce (données embarquées JSON) |

### Pourquoi ces sites ?

Le cahier des charges initial mentionnait BIM et Marjane. Après exploration technique :

- **BIM** — Pas de site e-commerce marocain avec prix accessibles
- **Marjane** — Données chargées via JavaScript (SPA React), nécessite Selenium/Playwright
- **MyMarket** — Pages HTML rendues côté serveur, structure stable et parseable avec BeautifulSoup
- **MarketPro** — Données produits embarquées en JSON directement dans le HTML (objet `dataLayer` GA4)

Ces deux enseignes couvrent les **mêmes catégories d'épicerie sèche**, ce qui permet la comparaison croisée.

---

## 2. Catégories collectées

| Catégorie | MyMarket | MarketPro |
|-----------|----------|-----------|
| Fruits secs | ✅ | ✅ |
| Épices | ✅ (page 2) | ✅ (pages 1 et 2) |
| Huiles & vinaigres | ✅ | ✅ |
| Pâtes | ✅ (page 2) | ✅ (pages 1 et 2, fusionné avec Riz) |
| Riz | ✅ | ✅ (dans "Pâtes et Riz") |
| Conserves | ✅ | ✅ (pages 1 et 2) |

---

## 3. Méthode technique

### 3.1 MyMarket — `scraper_mymarket.py`

**Technologie :** `requests` + `BeautifulSoup` (parser `lxml`)

**Fonctionnement :**

1. Requête HTTP GET sur chaque URL de catégorie avec un `User-Agent` standard
2. Parsing HTML : sélection des balises `<product-card class="card card-product">`
3. Extraction du nom (`<h2 class="card-heading">`) et du prix (`<span class="price-item">`)
4. Nettoyage du prix : suppression des unités `dh`, `ttc`, virgules → conversion `float`
5. Filtrage : prix nul ou > 5 000 MAD rejetés, doublons (même nom) ignorés
6. Extraction de la quantité par regex sur le nom du produit
7. Sauvegarde en `mymarket_products.json`

**Exemple de produit extrait :**
```json
{
  "nom": "Spaghetti N°5 Panzani 500 g",
  "prix": 25.29,
  "quantite": "500 G",
  "categorie": "Pâtes",
  "magasin": "MyMarket"
}
```

### 3.2 MarketPro — `scraper_marketpro.py`

**Technologie :** `requests` + extraction JSON depuis le HTML brut

**Fonctionnement :**

1. Requête HTTP GET sur chaque URL de catégorie (pages 1 et 2)
2. Recherche de la clé `"products":[` dans le HTML brut (objet `dataLayer` Google Analytics 4)
3. Extraction du tableau JSON par comptage de brackets imbriqués
4. Désérialisation et extraction des champs :
   - Nom : `title` ou `item_name` ou `name`
   - Prix : `price` (format GA4 direct) ou `prices.price / 100` (ancien format WooCommerce)
5. Déduplication par nom, sauvegarde en `marketpro_products.json`

**Exemple de produit extrait :**
```json
{
  "nom": "Spaghetti Panzani 500g",
  "prix": 15.0,
  "quantite": "500G",
  "categorie": "Pâtes et Riz",
  "magasin": "MarketPro"
}
```

---

## 4. Pipeline de nettoyage — `clean_products.py`

Les données brutes des scrapers passent par un pipeline de normalisation avant import en base.

### 4.1 Étapes de nettoyage

```
Données brutes JSON
       ↓
1. clean_text()         — unidecode, minuscules, caractères spéciaux
       ↓
2. Suppression marques  — regex \b<marque>\b (word-boundary, 60+ marques)
       ↓
3. Suppression stopwords — packaging, méthodes de préparation, descripteurs qualité
       ↓
4. Filtre tokens digits  — élimine "ndeg5", "4", "100" (tailles/numéros de format)
       ↓
5. CORRECTIONS          — pluriels → forme canonique (ex. "tranches" → "tranche")
       ↓
6. SINGULAR_MAP         — formes irrégulières (ex. "piments" → "piment")
       ↓
nom_normalise           — ex. "spaghetti", "huile olive", "champignon"
       ↓
7. generate_product_key() — MD5(nom_normalise + "_" + categorie_canonique)[:12]
```

### 4.2 Problèmes résolus

| Problème | Cause | Solution |
|----------|-------|----------|
| "hala" retiré de "halabi zaatar" | `str.replace()` sans délimiteur de mot | Regex `\b<marque>\b` |
| "spaghetti ndeg5" ≠ "spaghetti" | unidecode("N°5") = "ndeg5" | Filtre tokens contenant un chiffre |
| "champignon 4 4" ≠ "champignon" | "4/4" → "4 4" après substitution | Même filtre digits |
| total_initial gonflé (627 MAD) | get_pire_offre() = max absolu (bouteille 4L) | Pire offre = meilleur prix du magasin le plus cher |

### 4.3 Catégories canoniques

| Catégorie brute (scrapers) | Catégorie canonique (BDD) |
|---------------------------|--------------------------|
| Fruits secs | fruits secs |
| Épices | épices |
| Huiles & vinaigres / Huiles | huiles |
| Pâtes / Pâtes et Riz | féculents |
| Riz | féculents |
| Conserves | conserves |

---

## 5. Résultats

### Volume de données

| Métrique | Valeur |
|----------|--------|
| Produits uniques en base | **135** |
| Offres totales | **183** |
| Magasins | **2** (MyMarket, MarketPro) |
| Produits présents dans les 2 magasins | **18** |

### Répartition par magasin

| Magasin | Offres | Produits exclusifs |
|---------|--------|--------------------|
| MyMarket | ~100 | ~117 |
| MarketPro | ~83 | ~117 |

### Produits matchés entre les deux magasins (18)

| Catégorie | Produits | Magasin le moins cher |
|-----------|----------|-----------------------|
| Fruits secs | Pistaches, Amandes, Figues | MY (noix), MP (figues) |
| Épices | Cumin, Curcuma, Gingembre, Piment Doux, Piment Fort, Poivre Noir | MyMarket (2 à 7x moins cher) |
| Huiles | Huile olive, Huile de table | MyMarket |
| Féculents | Spaghetti, Penne, Tagliatelle, Riz | MarketPro |
| Conserves | Thon naturel, Thon à l'huile, Champignons | Variable |

---

## 6. Qualité des données

### Critères de validation appliqués

- Prix dans l'intervalle ]0, 5000[ MAD
- Nom produit non vide
- Déduplication par nom exact (scraping) puis par `product_key` (import en base)
- `qualite_score` par défaut à 5.0 (neutre) — pas de données qualité scrappées

### Limitations connues

- **Pas d'image produit** — les scrapers n'extraient pas les URLs d'images
- **Pas de lien produit** — pas de deeplink vers la fiche produit en magasin
- **Pas de stock réel** — le stock est fixé à 100 (valeur fictive) lors de l'import
- **Catégorie riz/pâtes fusionnée sur MarketPro** — séparation approximative par mots-clés
- **Pas de prix promotionnels** — le champ `promotion` est à `False` par défaut

---

## 7. Mise à jour des données

### Méthode manuelle (actuelle)

```bash
# 1. Relancer les scrapers
python app/scraper/scraper_mymarket.py
python app/scraper/scraper_marketpro.py

# 2. Nettoyer et normaliser
python app/scripts/clean_products.py

# 3. Réimporter en base (efface et recrée)
python seed.py
```

### Fréquence recommandée

Les prix de l'épicerie sèche sont stables (variations rares). Une mise à jour **hebdomadaire** est suffisante pour maintenir la pertinence des comparaisons.

### Perspective d'automatisation

Une tâche planifiée (cron job) pourrait automatiser les étapes ci-dessus. Cette fonctionnalité est identifiée comme amélioration future (hors scope Phase 4).

---

## 8. Fichiers produits

| Fichier | Description |
|---------|-------------|
| `app/scraper/scraper_mymarket.py` | Scraper MyMarket (BeautifulSoup) |
| `app/scraper/scraper_marketpro.py` | Scraper MarketPro (extraction JSON dataLayer) |
| `app/scraper/mymarket_products.json` | Données brutes MyMarket |
| `app/scraper/marketpro_products.json` | Données brutes MarketPro |
| `app/scripts/clean_products.py` | Pipeline de normalisation et génération des product_key |
| `data/mymarket_products_clean.json` | Données nettoyées MyMarket (prêtes pour seed.py) |
| `data/marketpro_products_clean.json` | Données nettoyées MarketPro (prêtes pour seed.py) |
| `seed.py` | Import en base PostgreSQL (Supabase) |
