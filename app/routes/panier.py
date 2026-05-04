from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.utils.security import get_current_user
from app.models import *
from app.schemas import PanierOptimiseResponse
from app.utils.security import get_current_user

router = APIRouter(prefix="/panier", tags=["Panier"])


@router.get("/optimise/{id_liste}", response_model=PanierOptimiseResponse)
def panier_optimise(
    id_liste: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):

    # 🔎 récupérer la liste
    liste = db.query(ListeCourses).filter(
        ListeCourses.id_listecourses == id_liste
    ).first()

    if not liste:
        raise HTTPException(status_code=404, detail="Liste non trouvée")

    # 🔐 vérifier que la liste appartient à l'utilisateur
    if liste.id_utilisateur != current_user.id_utilisateur:
        raise HTTPException(status_code=403, detail="Accès interdit")

    items = []
    total_optimise = 0
    total_classique = 0

    for ligne in liste.lignes:

        produit = ligne.produit

        offres = db.query(Offre).filter(
            Offre.id_produit == produit.id_produit
        ).all()

        if not offres:
            continue

        # ✅ FILTRER PAR STOCK
        offres_disponibles = [
            o for o in offres if o.stock >= ligne.quantite
        ]

        # ❌ aucun stock suffisant
        if not offres_disponibles:
            items.append({
                "produit": produit.nom_produit,
                "magasin": None,
                "prix": 0,
                "quantite": ligne.quantite,
                "total": 0
            })
            continue  # ✅ TRÈS IMPORTANT (doit être DANS le if)

        # ✅ meilleur prix
        meilleure_offre = min(offres_disponibles, key=lambda o: o.prix_offre)

        # ⚠️ pire prix dispo (pour comparaison)
        prix_classique = max(
            offres_disponibles, key=lambda o: o.prix_offre
        ).prix_offre

        magasin = db.query(Magasin).filter(
            Magasin.id_magasin == meilleure_offre.id_magasin
        ).first()

        total_item = meilleure_offre.prix_offre * ligne.quantite
        total_classique_item = prix_classique * ligne.quantite

        total_optimise += total_item
        total_classique += total_classique_item

        items.append({
            "produit": produit.nom_produit,
            "magasin": magasin.nom_magasin,
            "prix": meilleure_offre.prix_offre,
            "quantite": ligne.quantite,
            "total": total_item
        })

    economie = total_classique - total_optimise

    return {
        "items": items,
        "total_optimise": round(total_optimise, 2),
        "total_classique": round(total_classique, 2),
        "economie": round(economie, 2)
    }