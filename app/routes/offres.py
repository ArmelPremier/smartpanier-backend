from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db  # ✅ utiliser celui global
from app.models import *
from app.schemas import Offre as OffreSchema

router = APIRouter(prefix="/offres", tags=["Offres"])


@router.get("/{produit_id}")
def get_offres(produit_id: int, db: Session = Depends(get_db)):

    offres = db.query(Offre).filter(
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
            "magasin": o.magasin.nom_magasin  # 🔥 relation SQLAlchemy
        })

    return result