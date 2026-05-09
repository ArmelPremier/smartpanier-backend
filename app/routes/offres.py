from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Offre, HistoriquePrix
from app.schemas import Offre as OffreSchema

router = APIRouter(
    prefix="/offres",
    tags=["Offres"]
)


# =========================
# 🔥 OFFRES D'UN PRODUIT
# =========================
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

    produit_offres = db.query(Offre).filter(
        Offre.id_produit == id_produit
    ).all()

    if not produit_offres:
        raise HTTPException(
            status_code=404,
            detail="Aucune offre trouvée pour ce produit"
        )

    resultat = []

    for offre in produit_offres:

        historiques = db.query(HistoriquePrix).filter(
            HistoriquePrix.id_offre == offre.id_offre
        ).order_by(HistoriquePrix.date.asc()).all()

        historique_data = [
            {
                "date": h.date,
                "prix": h.prix
            }
            for h in historiques
        ]

        resultat.append({
            "id_offre": offre.id_offre,

            "magasin": (
                offre.magasin.nom_magasin
                if offre.magasin else "Inconnu"
            ),

            "prix_actuel": offre.prix_offre,

            "historique": historique_data
        })

    return {
        "id_produit": id_produit,
        "historique_prix": resultat
    }