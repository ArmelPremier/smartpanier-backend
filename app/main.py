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

app = FastAPI(
    title="SmartPanier API",
    description="API de comparaison de prix et optimisation de panier",
    version="1.0.0"
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