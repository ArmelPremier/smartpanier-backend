from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Offre, HistoriquePrix


router = APIRouter(
    prefix="/offres",
    tags=["Offres"]
)


# =========================
# 🔥 OFFRES D'UN PRODUIT
# =========================
@router.get("/produits/{produit_id}")
def get_offres(produit_id: int, db: Session = Depends(get_db)):
    return db.query(Offre).filter(
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
            "magasin": (
                o.magasin.nom_magasin
                if o.magasin else "Inconnu"
            )
        })

    return result


# =========================
# 📈 HISTORIQUE DES PRIX
# =========================
@router.get("/historique-prix/{id_produit}")
def historique_prix(id_produit: int, db: Session = Depends(get_db)):

    produits = db.query(Offre).filter(
        Offre.id_produit == id_produit
    ).all()

    if not produits:
        raise HTTPException(404, "Aucune offre trouvée")

    return {
        "id_produit": id_produit,
        "historique_prix": [
            {
                "id_offre": o.id_offre,
                "magasin": o.magasin.nom_magasin if o.magasin else "Inconnu",
                "prix_actuel": o.prix_offre,
                "historique": [
                    {
                        "date": h.date.isoformat(),
                        "prix": h.prix
                    }
                    for h in o.historiques
                ]
            }
            for o in produits
        ]
    }