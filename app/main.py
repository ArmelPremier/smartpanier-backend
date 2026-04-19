from fastapi import FastAPI
from app.database import engine, Base

# 🔹 Import des routes
from app.routes import produits, auth, offres

app = FastAPI(
    title="SmartPanier API",
    description="API de comparaison de prix et optimisation de panier",
    version="1.0.0"
)

# 🔹 Création des tables au démarrage
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


# 🔹 Route test
@app.get("/")
def home():
    return {"message": "API + Supabase OK 🚀"}


# 🔥 🔥 🔥 AJOUT DES ROUTES

app.include_router(produits.router)
app.include_router(auth.router)
app.include_router(offres.router)