from fastapi import FastAPI

from app.database import engine, Base

# 🔹 IMPORTANT
import app.models

from app.routes import (
    produits,
    auth,
    offres,
    optimisation,
    historique_optimisations,
    listes
)

description = """
## SmartPanier — Comparateur de prix & optimiseur de panier

SmartPanier analyse les prix de **MyMarket** et **MarketPro** pour vous aider à faire
vos courses au meilleur coût, avec 4 stratégies d'optimisation au choix.

### Fonctionnalités principales

- **Catalogue** : 135 produits scrapés et normalisés, répartis en 7 catégories
- **Offres multi-magasins** : prix en temps réel dans chaque enseigne
- **Optimisation** : 4 scénarios (voir section *Optimisation*)
- **Listes de courses** : créez, gérez et optimisez vos listes personnelles
- **Historique** : retrouvez toutes vos optimisations passées

### Authentification

Toutes les routes protégées nécessitent un token JWT.

1. `POST /login` → récupère `access_token`
2. Cliquez sur **Authorize** (cadenas) et entrez : `Bearer <access_token>`

### Scénarios d'optimisation

| Code | Stratégie |
|------|-----------|
| `prix_min` | Prix le plus bas, quel que soit le magasin |
| `mono_2_magasins` | Meilleure combinaison de 1 ou 2 magasins |
| `budget_strict` | Maximum d'articles dans le budget (tri par prix croissant) |
| `recommande` | Meilleur rapport qualité / prix |
"""

tags_metadata = [
    {
        "name": "Auth",
        "description": "Inscription, connexion et gestion du compte utilisateur (JWT).",
    },
    {
        "name": "Produits",
        "description": "Consultation du catalogue et recherche d'alternatives dans la même catégorie.",
    },
    {
        "name": "Offres",
        "description": "Prix disponibles par magasin pour un produit donné.",
    },
    {
        "name": "Listes",
        "description": "Création et gestion des listes de courses personnelles.",
    },
    {
        "name": "Optimisation",
        "description": "Calcul du panier optimal selon le scénario choisi.",
    },
    {
        "name": "Historique",
        "description": "Historique des paniers optimisés par liste.",
    },
]

app = FastAPI(
    title="SmartPanier API",
    description=description,
    version="1.0.0",
    openapi_tags=tags_metadata,
    contact={
        "name": "SmartPanier — Projet PI HICA",
        "email": "houenouarmel3@gmail.com",
    },
    license_info={
        "name": "MIT",
    },
)

# 🔹 ROUTES
app.include_router(produits.router)
app.include_router(auth.router)
app.include_router(offres.router)
app.include_router(optimisation.router)
app.include_router(listes.router)
app.include_router(historique_optimisations.router)

# =========================
# 🔹 DB INIT
# =========================
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

# =========================
# 🔹 TEST
# =========================
@app.get("/")
def home():
    return {"message": "API + Supabase OK 🚀"}