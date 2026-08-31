# SmartPanier — Backend

API REST qui compare les prix de produits d'épicerie entre deux supermarchés marocains (MyMarket et MarketPro) et calcule le panier le moins cher selon quatre stratégies d'optimisation.

## Contexte

Projet de fin d'année académique — **HICA 2025-2026** (Projet PI).
Backend développé par **Armel Houénou**.

## Fonctionnalités principales

- Authentification par compte utilisateur avec JWT (access token + refresh token)
- Catalogue de produits scrapés et normalisés depuis deux enseignes, répartis par catégorie
- Consultation des offres (prix par magasin) pour un produit donné
- Recherche d'alternatives (produits de la même catégorie, triés par prix)
- Création, modification, suppression et duplication de listes de courses personnelles
- Optimisation d'un panier selon 4 scénarios : `prix_min`, `mono_2_magasins`, `budget_strict`, `recommande`
- Filtre optionnel par magasins préférés lors de l'optimisation
- Historique des optimisations effectuées sur chaque liste
- Sauvegarde en base de chaque panier optimisé (résultat + détail par produit)
- Documentation interactive Swagger générée automatiquement

## Stack technique

D'après `requirements.txt` :

- **FastAPI** — framework API
- **Uvicorn** (extra `standard`) — serveur ASGI
- **SQLAlchemy** — ORM
- **psycopg2-binary** — driver PostgreSQL
- **python-jose[cryptography]** — génération/validation des tokens JWT
- **passlib[bcrypt]** + **bcrypt==4.0.1** — hachage des mots de passe
- **python-multipart** — support des formulaires FastAPI
- **python-dotenv** — chargement des variables d'environnement
- **requests** — scraping HTTP
- **beautifulsoup4** — parsing HTML (scraper MyMarket)
- **unidecode** — normalisation de texte (nettoyage des noms de produits)
- **pandas** — manipulation de données lors du nettoyage

Base de données : **PostgreSQL** (hébergée sur Supabase dans ce projet).

## Architecture

```
smartpanier-backend/
├── app/
│   ├── main.py                        # Point d'entrée FastAPI, déclaration des routers
│   ├── config.py                      # Lecture des variables d'environnement (JWT, etc.)
│   ├── database.py                    # Connexion PostgreSQL et session SQLAlchemy
│   ├── models.py                      # Modèles SQLAlchemy (8 tables)
│   ├── schemas.py                     # Schémas Pydantic (entrées/sorties des routes)
│   ├── test_db.py                     # Script de vérification de la connexion à la base
│   │
│   ├── routes/
│   │   ├── auth.py                    # Register, login, refresh, /me, changement de mot de passe
│   │   ├── produits.py                # Catalogue, alternatives, quantités d'une liste
│   │   ├── offres.py                  # Prix d'un produit par magasin
│   │   ├── listes.py                  # CRUD des listes de courses + lancement d'optimisation
│   │   ├── optimisation.py            # Les 4 algorithmes d'optimisation et la route /optimiser
│   │   └── historique_optimisations.py# Historique des paniers optimisés d'une liste
│   │
│   ├── services/
│   │   └── recommendation_service.py  # Recherche d'alternatives produit (même catégorie)
│   │
│   ├── scraper/
│   │   ├── scraper_mymarket.py        # Scraping MyMarket (BeautifulSoup)
│   │   └── scraper_marketpro.py       # Scraping MarketPro (extraction JSON dataLayer)
│   │
│   ├── scripts/
│   │   ├── clean_products.py          # Pipeline de normalisation (marque, quantité, product_key)
│   │   ├── import_marketpro.py        # Scrape + nettoie + importe MarketPro en base
│   │   ├── import_mymarket.py         # Scrape + nettoie + importe MyMarket en base
│   │   └── utils.py                   # Utilitaires de normalisation (non utilisés par clean_products.py)
│   │
│   └── utils/
│       └── security.py                # Hash de mot de passe, création/validation des JWT
│
├── data/                               # Données nettoyées prêtes pour l'import (JSON)
├── docs/
│   ├── schema.sql                      # DDL PostgreSQL complet (8 tables + index)
│   ├── scraping.md                     # Documentation détaillée du scraping et du nettoyage
│   └── presentation_backend.md         # Documentation de présentation du backend
├── seed.py                             # Importe les JSON nettoyés dans la base PostgreSQL
├── create_tables.py                    # Crée les tables à partir des modèles SQLAlchemy
├── create_demo_listes.py               # Génère des listes de démonstration via l'API
├── test_api.py                         # Script de tests d'intégration bout en bout de l'API
├── requirements.txt                    # Dépendances Python
├── render.yaml                         # Configuration de déploiement (Render)
└── start.sh                            # Commande de démarrage du serveur
```

## Schéma de données

8 tables SQLAlchemy (`app/models.py`), définies aussi dans `docs/schema.sql` :

| Table | Rôle |
|-------|------|
| `Utilisateur` | Comptes utilisateurs (nom, email unique, mot de passe haché) |
| `ListeCourses` | Liste de courses d'un utilisateur (nom, budget, date de création) |
| `LigneListeCourses` | Association produit/quantité au sein d'une liste |
| `Produit` | Catalogue de produits normalisés (nom, catégorie, marque, quantité, score qualité, `product_key` de matching) |
| `Magasin` | Enseigne (MyMarket, MarketPro) |
| `Offre` | Prix d'un produit dans un magasin (prix, promotion, stock, date de scraping) |
| `PanierOptimise` | Résultat d'une optimisation (total, économie, scénario utilisé) |
| `PanierOptimiseItem` | Détail produit par produit d'un panier optimisé (prix choisi, quantité, sous-total) |

## Logique métier : les 4 scénarios d'optimisation

Le point d'entrée commun (`preload_data()` dans `app/routes/optimisation.py`) charge en 3 requêtes SQL bulk les produits, offres et magasins nécessaires, puis chaque scénario applique sa propre stratégie :

- **`prix_min`** — pour chaque produit, prend l'offre la moins chère toutes enseignes confondues ; saute un produit si son ajout dépasse le budget.
- **`mono_2_magasins`** — teste chaque magasin seul puis toutes les combinaisons de 2 magasins, et retient la combinaison la moins chère qui couvre tous les produits dans le budget (erreur 400 sinon).
- **`budget_strict`** — trie les produits par sous-total croissant et les inclut un par un jusqu'à épuisement du budget, en utilisant toujours le prix le plus bas disponible.
- **`recommande`** — choisit pour chaque produit l'offre au meilleur ratio qualité/prix (`qualite_score / prix_offre`), sous réserve de stock suffisant et de budget disponible.

Un filtre optionnel `magasins_preferes` (liste d'IDs de magasins) peut être passé sur les 4 scénarios pour restreindre les offres considérées à certaines enseignes.

Chaque optimisation retourne `total`, `total_initial` (calculé à partir du meilleur prix du magasin le plus cher pour chaque produit), `economies` et la répartition par magasin, puis est sauvegardée en base (`PanierOptimise` + `PanierOptimiseItem`).

## Optimisation de performance : élimination des requêtes N+1

Avant correction, chaque scénario effectuait 3×N requêtes SQL en boucle (une requête produit, une requête offres, une requête nom de magasin par produit de la liste). Le correctif (commit `dd2471b`, fonction `preload_data()`) remplace cette boucle par 3 requêtes SQL bulk exécutées une seule fois avant le calcul.

Gains mesurés lors du commit (8 produits, base PostgreSQL distante sur Supabase) :

| Scénario | Avant | Après | Gain |
|----------|-------|-------|------|
| `prix_min` | 5877 ms | 3289 ms | **-44 %** |
| `mono_2_magasins` | 14891 ms | 3479 ms | **-77 %** |
| `budget_strict` | 7237 ms | 3383 ms | **-53 %** |
| `recommande` | 5787 ms | 3572 ms | **-38 %** |

La latence résiduelle est attribuée à la latence réseau vers la base de données distante.

## Endpoints API

Une documentation interactive complète (Swagger UI) est disponible sur **`/docs`** une fois le serveur lancé.

### Auth
- `POST /register` — créer un compte
- `POST /login` — connexion, retourne `access_token` et `refresh_token`
- `GET /me` — profil de l'utilisateur connecté
- `POST /refresh` — renouveler l'access token
- `PUT /change-password` — modifier le mot de passe

### Produits
- `GET /produits/` — catalogue complet
- `GET /produits/{id}/alternatives` — jusqu'à 3 alternatives dans la même catégorie
- `GET /produits/liste/{id_liste}/quantites` — produits et quantités d'une liste

### Offres
- `GET /offres/produits/{produit_id}` — prix d'un produit dans tous les magasins

### Listes de courses
- `POST /listes/` — créer une liste
- `GET /listes/me` — mes listes (historique)
- `GET /listes/{liste_id}` — détail d'une liste
- `GET /listes/me/last` — dernière liste créée
- `GET /listes/me/full` — profil + dernière liste + nombre total de listes
- `PUT /listes/{liste_id}` — modifier nom/budget
- `DELETE /listes/{liste_id}` — supprimer une liste
- `POST /listes/{liste_id}/produits` — ajouter un produit à la liste
- `DELETE /listes/{liste_id}/produits/{id_produit}` — retirer un produit
- `POST /listes/{liste_id}/duplicate` — dupliquer une liste

### Optimisation
- `GET /scenarios` — liste des 4 scénarios disponibles
- `POST /optimiser` — optimiser un panier libre (produits envoyés dans la requête)
- `POST /listes/{liste_id}/optimiser` — optimiser une liste sauvegardée

### Historique
- `GET /listes/{id_liste}/optimisations` — historique des optimisations d'une liste

## Installation

### Prérequis

- Python 3.10+ (testé avec la version indiquée dans `runtime.txt`)
- Une base PostgreSQL accessible (ex. Supabase)

### Étapes

```bash
# 1. Cloner le dépôt
git clone <url-du-depot>
cd smartpanier-backend

# 2. Créer et activer un environnement virtuel
python -m venv .venv
source .venv/bin/activate      # Linux/Mac
.venv\Scripts\activate         # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
cp .env.example .env
# Puis renseigner les valeurs dans .env
```

### Variables d'environnement (`.env`)

D'après `.env.example` :

| Variable | Description |
|----------|--------------|
| `DATABASE_URL` | URL de connexion PostgreSQL (ex. `postgresql://user:password@host:5432/postgres?sslmode=require`) |
| `SECRET_KEY` | Clé secrète utilisée pour signer les tokens JWT |
| `ALGORITHM` | Algorithme de signature JWT (défaut : `HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Durée de validité de l'access token, en minutes |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Durée de validité du refresh token, en jours |

### Initialiser la base de données

```bash
python create_tables.py
```

### Importer le catalogue de produits (optionnel)

Les données nettoyées sont déjà disponibles dans `data/`. Pour les importer en base :

```bash
python seed.py
```

### Lancer le serveur

```bash
uvicorn app.main:app --reload
```

L'API est alors accessible sur `http://localhost:8000`, la documentation Swagger sur `http://localhost:8000/docs`.

## Tests

Un script de tests d'intégration bout en bout est fourni (`test_api.py`), à exécuter serveur lancé :

```bash
uvicorn app.main:app --reload   # dans un terminal
python test_api.py              # dans un autre terminal
```

Il couvre l'authentification, le catalogue, les offres, les listes de courses, les 4 scénarios d'optimisation (via `/optimiser` et via `/listes/{id}/optimiser`) et l'historique. D'après `docs/presentation_backend.md`, la suite compte 33 vérifications, toutes passantes (33/33).

## Auteur

**Armel Houénou**
Élève ingénieur Data Science & IoT, SUP MTI
[LinkedIn](https://linkedin.com/in/armelhouenou) · [GitHub](https://github.com/ArmelPremier)

## Licence

MIT
