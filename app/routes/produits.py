from fastapi import APIRouter
from app.database import SessionLocal
from app.models import Produit

router = APIRouter()

@router.post("/produits")
def create_produit(nom: str, categorie: str):
    db = SessionLocal()

    produit = Produit(
        nom_produit=nom,
        categorie_produit=categorie
    )

    db.add(produit)
    db.commit()

    return produit

@router.get("/produits")
def get_produits():
    db = SessionLocal()
    return db.query(Produit).all()

@router.delete("/produits/{id}")
def delete_produit(id: int):
    db = SessionLocal()

    produit = db.query(Produit).get(id)
    db.delete(produit)
    db.commit()

    return {"message": "Deleted"}