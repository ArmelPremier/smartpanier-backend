from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Produit, Offre, Magasin

from app.schemas import (
    OptimisationRequest,
    OptimisationResponse,
    RepartitionMagasinResponse,
    ProduitOptimiseResponse,
    ScenarioResponse
)

router = APIRouter(
    prefix="",
    tags=["Optimisation"]
)

# =====================================================
# 🔥 HELPERS
# =====================================================

def get_produit(db, id_produit):
    return db.query(Produit).filter(
        Produit.id_produit == id_produit
    ).first()


def get_magasin(db, id_magasin):
    return db.query(Magasin).filter(
        Magasin.id_magasin == id_magasin
    ).first()


def get_offres(db, id_produit, quantite):

    return db.query(Offre).filter(
        Offre.id_produit == id_produit,
        Offre.stock >= quantite
    ).all()


def build_sous_total(offre, quantite):
    return offre.prix_offre * quantite


def ajouter_produit_repartition(
    repartition,
    magasin_nom,
    produit_response,
    sous_total
):

    if magasin_nom not in repartition:
        repartition[magasin_nom] = {
            "produits": [],
            "sous_total_magasin": 0
        }

    repartition[magasin_nom]["produits"].append(
        produit_response
    )

    repartition[magasin_nom][
        "sous_total_magasin"
    ] += sous_total


# =====================================================
# 📋 SCENARIOS DISPONIBLES
# =====================================================

@router.get(
    "/scenarios",
    response_model=list[ScenarioResponse]
)
def get_scenarios():

    return [

        {
            "code": "prix_min",
            "nom": "Prix minimum",
            "description":
            "Minimiser le coût total du panier"
        },

        {
            "code": "mono_2_magasins",
            "nom": "1 à 2 magasins",
            "description":
            "Réduire le nombre de magasins"
        },

        {
            "code": "budget_strict",
            "nom": "Budget strict",
            "description":
            "Respecter strictement le budget"
        },

        {
            "code": "recommande",
            "nom": "Panier recommandé",
            "description":
            "Meilleur rapport qualité/prix"
        }
    ]


# =====================================================
# 🟢 SCENARIO A — PRIX MINIMUM
# =====================================================

def scenario_prix_min(data, db):

    total = 0
    total_initial = 0

    repartition = {}

    for item in data.produits:

        produit = get_produit(
            db,
            item.id_produit
        )

        if not produit:
            continue

        offres = get_offres(
            db,
            item.id_produit,
            item.quantite
        )

        if not offres:
            continue

        meilleure_offre = min(
            offres,
            key=lambda o: o.prix_offre
        )

        pire_offre = max(
            offres,
            key=lambda o: o.prix_offre
        )

        sous_total = build_sous_total(
            meilleure_offre,
            item.quantite
        )

        sous_total_initial = build_sous_total(
            pire_offre,
            item.quantite
        )

        if total + sous_total > data.budget:
            raise HTTPException(
                status_code=400,
                detail="Budget dépassé"
            )

        total += sous_total
        total_initial += sous_total_initial

        magasin = get_magasin(
            db,
            meilleure_offre.id_magasin
        )

        produit_response = ProduitOptimiseResponse(
            id_produit=produit.id_produit,
            nom=produit.nom_produit,
            marque=produit.marque,
            qualite_score=produit.qualite_score,
            quantite=item.quantite,
            prix_unitaire=meilleure_offre.prix_offre,
            sous_total=sous_total
        )

        ajouter_produit_repartition(
            repartition,
            magasin.nom_magasin,
            produit_response,
            sous_total
        )

    return total, total_initial, repartition


# =====================================================
# 🟡 SCENARIO B — 1 OU 2 MAGASINS
# =====================================================

def scenario_1_2_magasins(data, db):

    magasins = db.query(Magasin).all()

    meilleur_total = float("inf")

    meilleure_repartition = None

    meilleur_total_initial = 0

    for magasin in magasins:

        total = 0
        total_initial = 0

        repartition = {}

        possible = True

        for item in data.produits:

            produit = get_produit(
                db,
                item.id_produit
            )

            if not produit:
                possible = False
                break

            offre = db.query(Offre).filter(
                Offre.id_produit == item.id_produit,
                Offre.id_magasin == magasin.id_magasin,
                Offre.stock >= item.quantite
            ).first()

            if not offre:
                possible = False
                break

            toutes_offres = get_offres(
                db,
                item.id_produit,
                item.quantite
            )

            pire_offre = max(
                toutes_offres,
                key=lambda o: o.prix_offre
            )

            sous_total = build_sous_total(
                offre,
                item.quantite
            )

            sous_total_initial = build_sous_total(
                pire_offre,
                item.quantite
            )

            if total + sous_total > data.budget:
                possible = False
                break

            total += sous_total
            total_initial += sous_total_initial

            produit_response = ProduitOptimiseResponse(
                id_produit=produit.id_produit,
                nom=produit.nom_produit,
                marque=produit.marque,
                qualite_score=produit.qualite_score,
                quantite=item.quantite,
                prix_unitaire=offre.prix_offre,
                sous_total=sous_total
            )

            ajouter_produit_repartition(
                repartition,
                magasin.nom_magasin,
                produit_response,
                sous_total
            )

        if possible and total < meilleur_total:

            meilleur_total = total
            meilleur_total_initial = total_initial

            meilleure_repartition = repartition

    if not meilleure_repartition:

        raise HTTPException(
            status_code=400,
            detail="Aucun magasin compatible"
        )

    return (
        meilleur_total,
        meilleur_total_initial,
        meilleure_repartition
    )


# =====================================================
# 🟠 SCENARIO C — BUDGET STRICT
# =====================================================

def scenario_budget_strict(data, db):

    produits_tries = []

    for item in data.produits:

        offres = get_offres(
            db,
            item.id_produit,
            item.quantite
        )

        if not offres:
            continue

        meilleure_offre = min(
            offres,
            key=lambda o: o.prix_offre
        )

        produits_tries.append({
            "item": item,
            "offre": meilleure_offre,
            "prix":
            meilleure_offre.prix_offre * item.quantite
        })

    produits_tries.sort(
        key=lambda x: x["prix"]
    )

    total = 0
    total_initial = 0

    repartition = {}

    for p in produits_tries:

        item = p["item"]
        offre = p["offre"]

        sous_total = p["prix"]

        if total + sous_total > data.budget:
            continue

        produit = get_produit(
            db,
            item.id_produit
        )

        magasin = get_magasin(
            db,
            offre.id_magasin
        )

        toutes_offres = get_offres(
            db,
            item.id_produit,
            item.quantite
        )

        pire_offre = max(
            toutes_offres,
            key=lambda o: o.prix_offre
        )

        sous_total_initial = build_sous_total(
            pire_offre,
            item.quantite
        )

        total += sous_total
        total_initial += sous_total_initial

        produit_response = ProduitOptimiseResponse(
            id_produit=produit.id_produit,
            nom=produit.nom_produit,
            marque=produit.marque,
            qualite_score=produit.qualite_score,
            quantite=item.quantite,
            prix_unitaire=offre.prix_offre,
            sous_total=sous_total
        )

        ajouter_produit_repartition(
            repartition,
            magasin.nom_magasin,
            produit_response,
            sous_total
        )

    if total == 0:

        raise HTTPException(
            status_code=400,
            detail="Budget insuffisant"
        )

    return total, total_initial, repartition


# =====================================================
# 🔵 SCENARIO D — PANIER RECOMMANDE
# =====================================================

def scenario_recommande(data, db):

    total = 0
    total_initial = 0

    repartition = {}

    for item in data.produits:

        produit = get_produit(
            db,
            item.id_produit
        )

        if not produit:
            continue

        offres = get_offres(
            db,
            item.id_produit,
            item.quantite
        )

        if not offres:
            continue

        meilleure_offre = max(
            offres,
            key=lambda o:
            produit.qualite_score /
            max(o.prix_offre, 0.1)
        )

        pire_offre = max(
            offres,
            key=lambda o: o.prix_offre
        )

        sous_total = build_sous_total(
            meilleure_offre,
            item.quantite
        )

        sous_total_initial = build_sous_total(
            pire_offre,
            item.quantite
        )

        if total + sous_total > data.budget:
            continue

        total += sous_total
        total_initial += sous_total_initial

        magasin = get_magasin(
            db,
            meilleure_offre.id_magasin
        )

        produit_response = ProduitOptimiseResponse(
            id_produit=produit.id_produit,
            nom=produit.nom_produit,
            marque=produit.marque,
            qualite_score=produit.qualite_score,
            quantite=item.quantite,
            prix_unitaire=meilleure_offre.prix_offre,
            sous_total=sous_total
        )

        ajouter_produit_repartition(
            repartition,
            magasin.nom_magasin,
            produit_response,
            sous_total
        )

    return total, total_initial, repartition


# =====================================================
# 🚀 ROUTE PRINCIPALE
# =====================================================

@router.post(
    "/optimiser",
    response_model=OptimisationResponse
)
def optimiser(
    data: OptimisationRequest,
    db: Session = Depends(get_db)
):

    if data.scenario == "prix_min":

        total, total_initial, repartition = (
            scenario_prix_min(data, db)
        )

    elif data.scenario == "mono_2_magasins":

        total, total_initial, repartition = (
            scenario_1_2_magasins(data, db)
        )

    elif data.scenario == "budget_strict":

        total, total_initial, repartition = (
            scenario_budget_strict(data, db)
        )

    elif data.scenario == "recommande":

        total, total_initial, repartition = (
            scenario_recommande(data, db)
        )

    else:

        raise HTTPException(
            status_code=400,
            detail="Scenario invalide"
        )

    repartition_list = [

        RepartitionMagasinResponse(
            magasin=nom_magasin,
            produits=data_magasin["produits"],
            sous_total_magasin=round(
                data_magasin["sous_total_magasin"],
                2
            )
        )

        for nom_magasin, data_magasin
        in repartition.items()
    ]

    return OptimisationResponse(

        total=round(total, 2),

        total_initial=round(
            total_initial,
            2
        ),

        economies=round(
            total_initial - total,
            2
        ),

        repartition=repartition_list
    )