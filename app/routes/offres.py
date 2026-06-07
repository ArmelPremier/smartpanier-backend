from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.database import get_db
from app.models import Offre


router = APIRouter(
    prefix="/offres",
    tags=["Offres"]
)


# =========================
# 🔥 OFFRES D'UN PRODUIT
# =========================
@router.get(
    "/produits/{produit_id}",
    summary="Prix d'un produit dans tous les magasins",
    description="Retourne la liste des offres disponibles (magasin + prix) pour un produit donné."
)
def get_offres(produit_id: int, db: Session = Depends(get_db)):
    offres = db.query(Offre).options(joinedload(Offre.magasin)).filter(
        Offre.id_produit == produit_id,
        Offre.stock > 0
    ).all()

    result = []

    for o in offres:
        result.append({
            "id_offre": o.id_offre,
            "prix": o.prix_offre,
            "promotion": o.promotion,
            "stock": o.stock,
            "magasin": o.magasin.nom_magasin if o.magasin else "Inconnu"
        })

    return result