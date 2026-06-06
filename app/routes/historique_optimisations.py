from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    ListeCourses,
    PanierOptimise
)

router = APIRouter(
    prefix="/listes",
    tags=["Historique Optimisations"]
)


# =====================================================
# 📜 HISTORIQUE DES OPTIMISATIONS D'UNE LISTE
# =====================================================

@router.get("/{id_liste}/optimisations")
def get_historique_optimisations(
    id_liste: int,
    db: Session = Depends(get_db)
):

    liste = db.query(ListeCourses).filter(
        ListeCourses.id_liste == id_liste
    ).first()

    if not liste:
        raise HTTPException(
            status_code=404,
            detail="Liste introuvable"
        )

    historiques = db.query(PanierOptimise).filter(
        PanierOptimise.id_liste == id_liste
    ).order_by(
        PanierOptimise.date_optimisation.desc()
    ).all()

    return [
        {
            "id_panier": panier.id_panier,
            "scenario": panier.scenario,
            "total_panier": panier.total_panier,
            "economie": panier.economie,
            "date_optimisation": panier.date_optimisation
        }
        for panier in historiques
    ]