from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import *
from app.schemas import ProduitCreate, ProduitResponse, AlternativeProduitResponse
from app.utils.security import get_current_user
from app.services.recommendation_service import trouver_alternatives

router = APIRouter(prefix="/produits", tags=["Produits"])


# =========================
# ✅ CREATE
# =========================
@router.post("/", response_model=ProduitResponse)
def create_produit(produit: ProduitCreate, db: Session = Depends(get_db)):
    new_produit = Produit(
    nom_produit=produit.nom_produit,
    categorie_produit=produit.categorie_produit,
    marque=produit.marque,
    qualite_score=produit.qualite_score
)

    db.add(new_produit)
    db.commit()
    db.refresh(new_produit)

    return new_produit


# =========================
# ✅ GET ALL
# =========================
@router.get("/", response_model=List[ProduitResponse])
def get_produits(db: Session = Depends(get_db)):
    produits = db.query(Produit).all()
    return produits


# =========================
# ✅ DELETE
# =========================
@router.delete("/{id}")
def delete_produit(id: int, db: Session = Depends(get_db)):
    produit = db.query(Produit).filter(Produit.id_produit == id).first()

    if not produit:
        raise HTTPException(status_code=404, detail="Produit non trouvé")

    db.delete(produit)
    db.commit()

    return {"message": "Produit supprimé"}

@router.get("/liste/{id_liste}/quantites")
def get_quantites(id_liste: int, db: Session = Depends(get_db)):
    lignes = db.query(LigneListeCourses).filter(
        LigneListeCourses.id_listecourses == id_liste
    ).all()

    return [
        {
            "produit": l.produit.nom_produit,
            "quantite": l.quantite
        }
        for l in lignes
    ]



@router.get(
    "/{id}/alternatives",
    response_model=List[AlternativeProduitResponse],
    summary="Alternatives à un produit",
    description="Retourne jusqu'à 3 produits alternatifs dans la même catégorie, triés par prix croissant."
)
def get_alternatives(
    id: int,
    budget_max: Optional[float] = None,
    db: Session = Depends(get_db)
):
    produit = db.query(Produit).filter(Produit.id_produit == id).first()
    if not produit:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    return trouver_alternatives(db, produit, budget_max)


@router.get("/me")
def get_profile(current_user: Utilisateur = Depends(get_current_user)):
    return {
        "nom": current_user.nom_utilisateur,
        "email": current_user.email_utilisateur
    }

@router.put("/me")
def update_profile(nom: str, db: Session = Depends(get_db),
                   current_user: Utilisateur = Depends(get_current_user)):

    current_user.nom_utilisateur = nom
    db.commit()

    return {"message": "Profil mis à jour"}

