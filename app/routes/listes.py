from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schemas import OptimisationRequest

from app.routes.optimisation import (
    scenario_prix_min,
    scenario_1_2_magasins,
    scenario_budget_strict,
    scenario_recommande,
    build_result
)

from app.database import get_db
from app.models import Utilisateur, ListeCourses, LigneListeCourses, Produit

from app.schemas import (
    ListeCoursesCreate,
    ListeCoursesResponse,
    HistoriqueListeResponse,
    ListeCoursesUpdate,
    AddProduitListeRequest
)
from sqlalchemy.orm import joinedload

from app.utils.security import get_current_user


router = APIRouter(
    prefix="/listes",
    tags=["Listes"]
)


# =====================================================
# 🛒 CRÉER UNE LISTE DE COURSES
# =====================================================

@router.post("/", response_model=ListeCoursesResponse, summary="Créer une liste de courses")
def create_liste(
    data: ListeCoursesCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):

    nouvelle_liste = ListeCourses(
        nom_liste=data.nom_liste,
        budget=data.budget,
        id_utilisateur=current_user.id_utilisateur
    )

    db.add(nouvelle_liste)
    db.commit()
    db.refresh(nouvelle_liste)

    # Ajouter les produits
    for item in data.produits:

        produit = db.query(Produit).filter(
            Produit.id_produit == item.id_produit
        ).first()

        if not produit:
            raise HTTPException(
                status_code=404,
                detail=f"Produit {item.id_produit} introuvable"
            )

        ligne = LigneListeCourses(
            id_liste=nouvelle_liste.id_liste,
            id_produit=item.id_produit,
            quantite=item.quantite
        )

        db.add(ligne)

    db.commit()
    db.refresh(nouvelle_liste)

    return nouvelle_liste


# =====================================================
# 📜 MES LISTES (HISTORIQUE)
# =====================================================

@router.get("/me", response_model=List[HistoriqueListeResponse], summary="Mes listes de courses")
def get_mes_listes(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):

    listes = db.query(ListeCourses)\
        .options(joinedload(ListeCourses.lignes))\
        .filter(
            ListeCourses.id_utilisateur == current_user.id_utilisateur
        ).all()

    return [
        HistoriqueListeResponse(
            id_liste=l.id_liste,
            nom_liste=l.nom_liste,
            budget=l.budget,
            date_creation=str(l.date_creation),
            nombre_produits=len(l.lignes)
        )
        for l in listes
    ]


# =====================================================
# 📄 DÉTAIL D’UNE LISTE
# =====================================================

@router.get(
    "/{liste_id}",
    response_model=ListeCoursesResponse,
    summary="Détail d'une liste",
    description="Retourne le contenu complet d'une liste de courses (produits + quantités).",
)
def get_liste(
    liste_id: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):

    liste = db.query(ListeCourses).filter(
        ListeCourses.id_liste == liste_id,
        ListeCourses.id_utilisateur == current_user.id_utilisateur
    ).first()

    if not liste:
        raise HTTPException(
            status_code=404,
            detail="Liste introuvable"
        )

    return liste

def get_last_liste(db, user_id):
    return (
        db.query(ListeCourses)
        .options(joinedload(ListeCourses.lignes))
        .filter(ListeCourses.id_utilisateur == user_id)
        .order_by(ListeCourses.date_creation.desc())
        .first()
    )

@router.get(
    "/me/full",
    summary="Profil utilisateur + dernière liste",
    description="Retourne le profil de l'utilisateur connecté, sa dernière liste et le nombre total de listes.",
)
def get_me_full(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):

    # 👤 utilisateur
    user = {
        "id": current_user.id_utilisateur,
        "nom": current_user.nom_utilisateur,
        "email": current_user.email_utilisateur
    }

    # 🧺 dernière liste
    last_liste = get_last_liste(db, current_user.id_utilisateur)

    if last_liste:
        derniere_liste = {
            "id_liste": last_liste.id_liste,
            "nom_liste": last_liste.nom_liste,
            "budget": last_liste.budget,
            "date_creation": str(last_liste.date_creation),
            "produits": [
                {
                    "id_produit": l.id_produit,
                    "quantite": l.quantite
                }
                for l in last_liste.lignes
            ]
        }
    else:
        derniere_liste = None

    # 📊 nombre total de listes
    total_listes = db.query(ListeCourses).filter(
        ListeCourses.id_utilisateur == current_user.id_utilisateur
    ).count()

    return {
        "user": user,
        "derniere_liste": derniere_liste,
        "total_listes": total_listes
    }

@router.get(
    "/me/last",
    response_model=ListeCoursesResponse,
    summary="Dernière liste de courses",
    description="Retourne la liste de courses la plus récemment créée par l'utilisateur connecté.",
)
def get_ma_derniere_liste(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):

    last_liste = get_last_liste(db, current_user.id_utilisateur)

    if not last_liste:
        raise HTTPException(
            status_code=404,
            detail="Aucune liste trouvée"
        )

    return last_liste

def serialize_liste(liste):
    return {
        "id_liste": liste.id_liste,
        "nom_liste": liste.nom_liste,
        "budget": liste.budget,
        "date_creation": str(liste.date_creation),
        "produits": [
            {
                "id_produit": l.id_produit,
                "quantite": l.quantite
            }
            for l in liste.lignes
        ]
    }


# =====================================================
# 🗑️ SUPPRIMER UNE LISTE
# =====================================================

@router.delete(
    "/{liste_id}",
    summary="Supprimer une liste",
    description="Supprime définitivement une liste et toutes ses lignes.",
)
def delete_liste(
    liste_id: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):

    liste = db.query(ListeCourses).filter(
        ListeCourses.id_liste == liste_id,
        ListeCourses.id_utilisateur == current_user.id_utilisateur
    ).first()

    if not liste:
        raise HTTPException(
            status_code=404,
            detail="Liste introuvable"
        )

    db.delete(liste)
    db.commit()

    return {"message": "Liste supprimée avec succès"}

# =====================================================
# ✏️ MODIFIER UNE LISTE
# =====================================================

@router.put(
    "/{liste_id}",
    response_model=ListeCoursesResponse,
    summary="Modifier une liste",
    description="Met à jour le nom et/ou le budget d'une liste existante.",
)
def update_liste(
    liste_id: int,
    data: ListeCoursesUpdate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):

    liste = db.query(ListeCourses).filter(
        ListeCourses.id_liste == liste_id,
        ListeCourses.id_utilisateur == current_user.id_utilisateur
    ).first()

    if not liste:
        raise HTTPException(
            status_code=404,
            detail="Liste introuvable"
        )

    if data.nom_liste is not None:
        liste.nom_liste = data.nom_liste

    if data.budget is not None:
        liste.budget = data.budget

    db.commit()
    db.refresh(liste)

    return liste
    

# =====================================================
# ➕ AJOUTER PRODUIT À UNE LISTE
# =====================================================

@router.post(
    "/{liste_id}/produits",
    summary="Ajouter un produit à la liste",
    description="Ajoute un produit avec sa quantité. Si le produit est déjà présent, la quantité est cumulée.",
)
def add_produit_to_liste(
    liste_id: int,
    data: AddProduitListeRequest,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):

    # 🔎 Vérifier liste
    liste = db.query(ListeCourses).filter(
        ListeCourses.id_liste == liste_id,
        ListeCourses.id_utilisateur == current_user.id_utilisateur
    ).first()

    if not liste:
        raise HTTPException(
            status_code=404,
            detail="Liste introuvable"
        )

    # 🔎 Vérifier produit
    produit = db.query(Produit).filter(
        Produit.id_produit == data.id_produit
    ).first()

    if not produit:
        raise HTTPException(
            status_code=404,
            detail="Produit introuvable"
        )

    # 🔎 Vérifier si produit déjà présent
    existing_line = db.query(LigneListeCourses).filter(
        LigneListeCourses.id_liste == liste_id,
        LigneListeCourses.id_produit == data.id_produit
    ).first()

    # 🔥 Si produit déjà présent → augmenter quantité
    if existing_line:
        existing_line.quantite += data.quantite

    else:
        nouvelle_ligne = LigneListeCourses(
            id_liste=liste_id,
            id_produit=data.id_produit,
            quantite=data.quantite
        )

        db.add(nouvelle_ligne)

    db.commit()

    return {
        "message": "Produit ajouté à la liste"
    }

# =====================================================
# ❌ SUPPRIMER PRODUIT D’UNE LISTE
# =====================================================

@router.delete(
    "/{liste_id}/produits/{id_produit}",
    summary="Retirer un produit de la liste",
    description="Supprime une ligne produit de la liste de courses.",
)
def remove_produit_from_liste(
    liste_id: int,
    id_produit: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):

    # 🔎 Vérifier liste utilisateur
    liste = db.query(ListeCourses).filter(
        ListeCourses.id_liste == liste_id,
        ListeCourses.id_utilisateur == current_user.id_utilisateur
    ).first()

    if not liste:
        raise HTTPException(
            status_code=404,
            detail="Liste introuvable"
        )

    # 🔎 Rechercher ligne produit
    ligne = db.query(LigneListeCourses).filter(
        LigneListeCourses.id_liste == liste_id,
        LigneListeCourses.id_produit == id_produit
    ).first()

    if not ligne:
        raise HTTPException(
            status_code=404,
            detail="Produit absent de la liste"
        )

    db.delete(ligne)
    db.commit()

    return {
        "message": "Produit supprimé de la liste"
    }

# =====================================================
# 📄 DUPLIQUER UNE LISTE
# =====================================================

@router.post(
    "/{liste_id}/duplicate",
    summary="Dupliquer une liste",
    description="Crée une copie de la liste avec tous ses produits. La copie porte le nom original suivi de '(copie)'.",
)
def duplicate_liste(
    liste_id: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):

    # 🔎 Vérifier liste
    liste = db.query(ListeCourses).filter(
        ListeCourses.id_liste == liste_id,
        ListeCourses.id_utilisateur == current_user.id_utilisateur
    ).first()

    if not liste:
        raise HTTPException(
            status_code=404,
            detail="Liste introuvable"
        )

    # 🔥 Créer nouvelle liste
    nouvelle_liste = ListeCourses(
        nom_liste=f"{liste.nom_liste} (copie)",
        budget=liste.budget,
        id_utilisateur=current_user.id_utilisateur
    )

    db.add(nouvelle_liste)
    db.commit()
    db.refresh(nouvelle_liste)

    # 🔥 Copier produits
    for ligne in liste.lignes:

        nouvelle_ligne = LigneListeCourses(
            id_liste=nouvelle_liste.id_liste,
            id_produit=ligne.id_produit,
            quantite=ligne.quantite
        )

        db.add(nouvelle_ligne)

    db.commit()

    return {
        "message": "Liste dupliquée avec succès",
        "nouvelle_liste_id": nouvelle_liste.id_liste
    }

# =====================================================
# 🧠 OPTIMISER UNE LISTE
# =====================================================

@router.post(
    "/{liste_id}/optimiser",
    summary="Optimiser une liste existante",
    description="Lance l'optimisation directement depuis la liste sauvegardée. Le budget utilisé est celui de la liste.",
)
def optimiser_liste(
    liste_id: int,
    scenario: str,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):

    # 🔎 Vérifier liste
    liste = db.query(ListeCourses).filter(
        ListeCourses.id_liste == liste_id,
        ListeCourses.id_utilisateur == current_user.id_utilisateur
    ).first()

    if not liste:
        raise HTTPException(
            status_code=404,
            detail="Liste introuvable"
        )

    # 🔥 Construire produits optimisation
    produits = []

    for ligne in liste.lignes:
        produits.append({
            "id_produit": ligne.id_produit,
            "quantite": ligne.quantite
        })

    # 🔥 Construire request optimisation
    optimisation_data = OptimisationRequest(
        id_liste=liste.id_liste,
        budget=liste.budget or 999999,
        scenario=scenario,
        produits=produits
    )

    # =================================================
    # 🚀 LANCER SCENARIO
    # =================================================

    if scenario == "prix_min":

        total, initial, rep = scenario_prix_min(
            optimisation_data,
            db
        )

    elif scenario == "mono_2_magasins":

        total, initial, rep = scenario_1_2_magasins(
            optimisation_data,
            db
        )

    elif scenario == "budget_strict":

        total, initial, rep = scenario_budget_strict(
            optimisation_data,
            db
        )

    elif scenario == "recommande":

        total, initial, rep = scenario_recommande(
            optimisation_data,
            db
        )

    else:
        raise HTTPException(
            status_code=400,
            detail="Scenario invalide"
        )

    return build_result(total, initial, rep)