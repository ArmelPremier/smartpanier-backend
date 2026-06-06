from itertools import combinations as itertools_combinations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Produit, Offre, Magasin, ListeCourses, PanierOptimise, PanierOptimiseItem

from app.schemas import (
    OptimisationRequest,
    OptimisationResponse,
    RepartitionMagasinResponse,
    ProduitOptimiseResponse,
    ScenarioResponse
)

router = APIRouter(prefix="", tags=["Optimisation"])


# =====================================================
# HELPERS
# =====================================================

def get_produit(db, id_produit):
    return db.query(Produit).filter(
        Produit.id_produit == id_produit
    ).first()


def get_magasin_nom(db, id_magasin):
    m = db.query(Magasin).filter(
        Magasin.id_magasin == id_magasin
    ).first()
    return m.nom_magasin if m else "Inconnu"


def get_offres(db, id_produit):
    return db.query(Offre).filter(
        Offre.id_produit == id_produit,
        Offre.stock > 0
    ).all()


def get_meilleure_offre(offres):
    return min(offres, key=lambda o: o.prix_offre)


def get_pire_offre(offres):
    return max(offres, key=lambda o: o.prix_offre)


def score_recommande(produit, offre):
    return produit.qualite_score / max(offre.prix_offre, 0.1)


def build_produit_response(produit, offre, quantite):
    return ProduitOptimiseResponse(
        id_produit=produit.id_produit,
        nom=produit.nom_produit,
        marque=produit.marque,
        qualite_score=produit.qualite_score,
        quantite=quantite,
        prix_unitaire=offre.prix_offre,
        sous_total=round(offre.prix_offre * quantite, 2)
    )


def ajouter_produit_repartition(repartition, magasin_nom, produit_resp):
    if magasin_nom not in repartition:
        repartition[magasin_nom] = {
            "produits": [],
            "sous_total_magasin": 0
        }
    repartition[magasin_nom]["produits"].append(produit_resp)
    repartition[magasin_nom]["sous_total_magasin"] += produit_resp.sous_total


def build_result(total, total_initial, repartition):
    return OptimisationResponse(
        total=round(total, 2),
        total_initial=round(total_initial, 2),
        economies=round(total_initial - total, 2),
        repartition=[
            RepartitionMagasinResponse(
                magasin=nom,
                produits=data["produits"],
                sous_total_magasin=round(data["sous_total_magasin"], 2)
            )
            for nom, data in repartition.items()
        ]
    )


# =====================================================
# SCENARIOS
# =====================================================

@router.get(
    "/scenarios",
    response_model=list[ScenarioResponse],
    summary="Liste des scénarios d'optimisation disponibles"
)
def get_scenarios():
    return [
        {"code": "prix_min",        "nom": "Prix minimum",      "description": "Minimiser le coût total en achetant chaque produit au prix le plus bas, quel que soit le magasin"},
        {"code": "mono_2_magasins", "nom": "1 à 2 magasins",    "description": "Réduire le nombre de visites en trouvant la meilleure combinaison de 1 ou 2 magasins"},
        {"code": "budget_strict",   "nom": "Budget strict",     "description": "Inclure le maximum de produits possible sans dépasser le budget, en priorité les moins chers"},
        {"code": "recommande",      "nom": "Panier recommandé", "description": "Meilleur rapport qualité/prix en tenant compte du score qualité de chaque produit"},
    ]


# =====================================================
# SCENARIO 1 — PRIX MINIMUM
# Acheter chaque produit au prix le plus bas toutes
# enseignes confondues. Saute un produit si son ajout
# dépasse le budget.
# =====================================================

def scenario_prix_min(data, db):
    total = 0
    total_initial = 0
    repartition = {}

    for item in data.produits:

        produit = get_produit(db, item.id_produit)
        if not produit:
            continue

        offres = get_offres(db, item.id_produit)
        if not offres:
            continue

        meilleure = get_meilleure_offre(offres)
        pire      = get_pire_offre(offres)

        sous_total         = meilleure.prix_offre * item.quantite
        sous_total_initial = pire.prix_offre      * item.quantite

        # Sauter ce produit s'il fait dépasser le budget
        if data.budget and total + sous_total > data.budget:
            continue

        total         += sous_total
        total_initial += sous_total_initial

        magasin_nom  = get_magasin_nom(db, meilleure.id_magasin)
        produit_resp = build_produit_response(produit, meilleure, item.quantite)
        ajouter_produit_repartition(repartition, magasin_nom, produit_resp)

    return total, total_initial, repartition


# =====================================================
# SCENARIO 2 — 1 OU 2 MAGASINS
# Essaie d'abord chaque magasin seul, puis toutes les
# paires. Retient la combinaison la moins chère qui
# couvre tous les produits dans le budget.
# =====================================================

def scenario_1_2_magasins(data, db):
    magasins = db.query(Magasin).all()

    # Génère toutes les combinaisons : 1 magasin puis paires de 2
    candidats = [[m] for m in magasins] + [
        list(combo) for combo in itertools_combinations(magasins, 2)
    ]

    best_total   = float("inf")
    best_initial = 0
    best_rep     = None

    for combo in candidats:

        total         = 0
        total_initial = 0
        repartition   = {}
        valide        = True

        for item in data.produits:

            produit = get_produit(db, item.id_produit)
            if not produit:
                valide = False
                break

            # Meilleure offre parmi les magasins de la combinaison
            offre_choisie = None
            for m in combo:
                offre = db.query(Offre).filter(
                    Offre.id_produit  == item.id_produit,
                    Offre.id_magasin  == m.id_magasin,
                    Offre.stock       >  0
                ).order_by(Offre.prix_offre).first()

                if offre and (offre_choisie is None or offre.prix_offre < offre_choisie.prix_offre):
                    offre_choisie = offre

            if not offre_choisie:
                valide = False
                break

            sous_total = offre_choisie.prix_offre * item.quantite

            if data.budget and total + sous_total > data.budget:
                valide = False
                break

            toutes_offres = get_offres(db, item.id_produit)
            pire = get_pire_offre(toutes_offres) if toutes_offres else offre_choisie

            total         += sous_total
            total_initial += pire.prix_offre * item.quantite

            magasin_nom  = get_magasin_nom(db, offre_choisie.id_magasin)
            produit_resp = build_produit_response(produit, offre_choisie, item.quantite)
            ajouter_produit_repartition(repartition, magasin_nom, produit_resp)

        if valide and total < best_total:
            best_total   = total
            best_initial = total_initial
            best_rep     = repartition

    if not best_rep:
        raise HTTPException(
            status_code=400,
            detail="Aucune combinaison de 1 à 2 magasins ne couvre tous les produits dans le budget"
        )

    return best_total, best_initial, best_rep


# =====================================================
# SCENARIO 3 — BUDGET STRICT
# Trie les produits par sous-total croissant et les
# inclut un par un jusqu'à épuisement du budget.
# Utilise toujours le prix le plus bas disponible.
# =====================================================

def scenario_budget_strict(data, db):

    candidats = []

    for item in data.produits:

        offres = get_offres(db, item.id_produit)
        if not offres:
            continue

        meilleure = get_meilleure_offre(offres)
        pire      = get_pire_offre(offres)
        sous_total = meilleure.prix_offre * item.quantite

        candidats.append((item, meilleure, pire, sous_total))

    # Priorité aux produits les moins chers pour maximiser le nombre d'articles
    candidats.sort(key=lambda x: x[3])

    total         = 0
    total_initial = 0
    repartition   = {}

    for item, offre, pire, sous_total in candidats:

        if total + sous_total > data.budget:
            continue

        produit = get_produit(db, item.id_produit)
        if not produit:
            continue

        total         += sous_total
        total_initial += pire.prix_offre * item.quantite

        magasin_nom  = get_magasin_nom(db, offre.id_magasin)
        produit_resp = build_produit_response(produit, offre, item.quantite)
        ajouter_produit_repartition(repartition, magasin_nom, produit_resp)

    if total == 0:
        raise HTTPException(
            status_code=400,
            detail="Budget insuffisant pour inclure au moins un produit"
        )

    return total, total_initial, repartition


# =====================================================
# SCENARIO 4 — RECOMMANDÉ
# Choisit l'offre avec le meilleur score qualité/prix
# pour chaque produit. Saute un produit si son ajout
# dépasse le budget.
# =====================================================

def scenario_recommande(data, db):
    total         = 0
    total_initial = 0
    repartition   = {}

    for item in data.produits:

        produit = get_produit(db, item.id_produit)
        if not produit:
            continue

        offres = get_offres(db, item.id_produit)
        if not offres:
            continue

        meilleure = max(offres, key=lambda o: score_recommande(produit, o))
        pire      = get_pire_offre(offres)

        sous_total         = meilleure.prix_offre * item.quantite
        sous_total_initial = pire.prix_offre      * item.quantite

        # Vérification stock et budget AVANT de modifier les totaux
        if meilleure.stock < item.quantite:
            continue

        if data.budget and total + sous_total > data.budget:
            continue

        total         += sous_total
        total_initial += sous_total_initial

        magasin_nom  = get_magasin_nom(db, meilleure.id_magasin)
        produit_resp = build_produit_response(produit, meilleure, item.quantite)
        ajouter_produit_repartition(repartition, magasin_nom, produit_resp)

    return total, total_initial, repartition


# =====================================================
# ROUTE PRINCIPALE
# =====================================================

@router.post(
    "/optimiser",
    response_model=OptimisationResponse,
    summary="Optimiser un panier de courses",
    description=(
        "Calcule la meilleure répartition d'achats selon le scénario choisi. "
        "Retourne le total optimisé, les économies réalisées et la répartition par magasin."
    )
)
def optimiser(data: OptimisationRequest, db: Session = Depends(get_db)):

    if data.scenario == "prix_min":
        total, initial, rep = scenario_prix_min(data, db)

    elif data.scenario == "mono_2_magasins":
        total, initial, rep = scenario_1_2_magasins(data, db)

    elif data.scenario == "budget_strict":
        total, initial, rep = scenario_budget_strict(data, db)

    elif data.scenario == "recommande":
        total, initial, rep = scenario_recommande(data, db)

    else:
        raise HTTPException(status_code=400, detail="Scénario invalide")

    result = build_result(total, initial, rep)

    # =====================================================
    # SAUVEGARDE EN BASE
    # =====================================================

    liste = db.query(ListeCourses).filter(
        ListeCourses.id_liste == data.id_liste
    ).first()

    if not liste:
        raise HTTPException(status_code=404, detail="Liste introuvable")

    panier = PanierOptimise(
        total_panier=result.total,
        economie=result.economies,
        scenario=data.scenario,
        id_liste=liste.id_liste
    )

    db.add(panier)
    db.commit()
    db.refresh(panier)

    for magasin_data in result.repartition:

        magasin = db.query(Magasin).filter(
            Magasin.nom_magasin == magasin_data.magasin
        ).first()

        for produit in magasin_data.produits:

            db.add(PanierOptimiseItem(
                id_panier=panier.id_panier,
                id_produit=produit.id_produit,
                id_magasin=magasin.id_magasin,
                prix_choisi=produit.prix_unitaire,
                quantite=produit.quantite,
                sous_total=produit.sous_total
            ))

    db.commit()

    return result
