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
from app.services.recommendation_service import trouver_alternative



router = APIRouter(prefix="", tags=["Optimisation"])

@router.get("/scenarios", response_model=list[ScenarioResponse])
def get_scenarios():
    return [
        {
            "code": "economique",
            "nom": "Économique",
            "description": "Minimiser le coût total en choisissant les offres les moins chères"
        },
        {
            "code": "mono_magasin",
            "nom": "Un seul magasin",
            "description": "Acheter tous les produits dans un seul magasin"
        },
        {
            "code": "equilibre",
            "nom": "Équilibré",
            "description": "Compromis entre prix et nombre de magasins"
        },
        {
            "code": "qualite",
            "nom": "Qualité",
            "description": "Favoriser certains magasins préférés"
        },
        {
            "code": "budget_strict",
            "nom": "Budget strict",
            "description": "Respect strict du budget avec priorisation des produits essentiels"
        },
        {
            "code": "recommande",
            "nom": "Panier recommandé",
            "description": "Recommandation basée sur qualité/prix"
        },]


@router.post("/optimiser", response_model=OptimisationResponse)
def optimiser(data: OptimisationRequest, db: Session = Depends(get_db)):

    if data.scenario not in ["economique","mono_magasin","qualite","equilibre","budget_strict","recommande"]:
        raise HTTPException(status_code=400, detail="Scenario invalide")

    budget = data.budget

    # =========================
    # 🔥 SCENARIO ECONOMIQUE
    # =========================
    if data.scenario == "economique":

        repartition = {}
        total = 0
        total_classique = 0

        for item in data.produits:

            produit = db.query(Produit).filter(
                Produit.id_produit == item.id_produit
            ).first()

            if not produit:
                raise HTTPException(
                    status_code=404,
                    detail=f"Produit {item.id_produit} introuvable"
                )

            offres = db.query(Offre).filter(
                Offre.id_produit == produit.id_produit
            ).all()

            if not offres:
                continue

            # 🔥 filtrer par stock
            offres_disponibles = [
                o for o in offres if o.stock >= item.quantite
            ]

            if not offres_disponibles:
                continue

            # ✅ meilleur prix
            meilleure_offre = min(
                offres_disponibles,
                key=lambda o: o.prix_offre
            )

            # ⚠️ pire prix (pour économie)
            pire_offre = max(
                offres_disponibles,
                key=lambda o: o.prix_offre
            )

            magasin = db.query(Magasin).filter(
                Magasin.id_magasin == meilleure_offre.id_magasin
            ).first()

            if not magasin:
                continue

            sous_total = meilleure_offre.prix_offre * item.quantite
            sous_total_classique = pire_offre.prix_offre * item.quantite

            # 🚨 CONTRÔLE BUDGET (IMPORTANT)
            if total + sous_total > budget:
                raise HTTPException(
                    status_code=400,
                    detail=f"Budget dépassé ❌ (budget={budget} MAD)"
                )

            total += sous_total
            total_classique += sous_total_classique

            # 🔥 regroupement par magasin
            if magasin.nom_magasin not in repartition:
                repartition[magasin.nom_magasin] = {
                    "produits": [],
                    "sous_total_magasin": 0
                }

            repartition[magasin.nom_magasin]["produits"].append(
                ProduitOptimiseResponse(
                    id_produit=produit.id_produit,
                    nom=produit.nom_produit,
                    quantite=item.quantite,
                    prix_unitaire=meilleure_offre.prix_offre,
                    sous_total=sous_total
                )
            )

            repartition[magasin.nom_magasin]["sous_total_magasin"] += sous_total

        repartition_list = [
            RepartitionMagasinResponse(
                magasin=nom_magasin,
                produits=data_magasin["produits"],
                sous_total_magasin=round(data_magasin["sous_total_magasin"], 2)
            )
            for nom_magasin, data_magasin in repartition.items()
        ]

        return OptimisationResponse(
            total=round(total, 2),
            economies=round(total_classique - total, 2),
            repartition=repartition_list
        )

    # =========================
    # 🏪 SCENARIO MONO MAGASIN
    # =========================
    elif data.scenario == "mono_magasin":

        magasins = db.query(Magasin).all()
        meilleur_total = float("inf")
        meilleure_repartition = None

        for magasin in magasins:

            total_magasin = 0
            produits_magasin = []
            possible = True

            for item in data.produits:

                offre = db.query(Offre).filter(
                    Offre.id_produit == item.id_produit,
                    Offre.id_magasin == magasin.id_magasin,
                    Offre.stock >= item.quantite
                ).first()

                if not offre:
                    possible = False
                    break

                produit = db.query(Produit).filter(
                    Produit.id_produit == item.id_produit
                ).first()

                sous_total = offre.prix_offre * item.quantite

                # 🚨 CONTRÔLE BUDGET
                if total_magasin + sous_total > budget:
                    possible = False
                    break

                total_magasin += sous_total

                produits_magasin.append(
                    ProduitOptimiseResponse(
                        id_produit=produit.id_produit,
                        nom=produit.nom_produit,
                        quantite=item.quantite,
                        prix_unitaire=offre.prix_offre,
                        sous_total=sous_total
                    )
                )

            if possible and total_magasin < meilleur_total:
                meilleur_total = total_magasin
                meilleure_repartition = RepartitionMagasinResponse(
                    magasin=magasin.nom_magasin,
                    produits=produits_magasin,
                    sous_total_magasin=round(total_magasin, 2)
                )

        if not meilleure_repartition:
            raise HTTPException(
                status_code=400,
                detail="Aucun magasin ne respecte le budget ou le stock"
            )

        return OptimisationResponse(
            total=round(meilleur_total, 2),
            economies=0,
            repartition=[meilleure_repartition]
        )

        # =========================
    # ⚖️ SCENARIO EQUILIBRE
    # =========================
    elif data.scenario == "equilibre":

        repartition = {}
        total = 0
        total_classique = 0

        magasins_utilises = set()

        for item in data.produits:

            produit = db.query(Produit).filter(
                Produit.id_produit == item.id_produit
            ).first()

            if not produit:
                raise HTTPException(
                    status_code=404,
                    detail=f"Produit {item.id_produit} introuvable"
                )

            offres = db.query(Offre).filter(
                Offre.id_produit == produit.id_produit
            ).all()

            if not offres:
                continue

            # 🔥 filtrer stock
            offres_disponibles = [
                o for o in offres if o.stock >= item.quantite
            ]

            if not offres_disponibles:
                continue

            meilleure_offre = None
            meilleur_score = float("inf")

            for offre in offres_disponibles:

                magasin = db.query(Magasin).filter(
                    Magasin.id_magasin == offre.id_magasin
                ).first()

                if not magasin:
                    continue

                prix = offre.prix_offre

                # ⚖️ pénalité si nouveau magasin
                penalite_magasin = 5 if magasin.nom_magasin not in magasins_utilises else 0

                # 🎯 bonus promo
                bonus_promo = 2 if offre.promotion else 0

                score = prix + penalite_magasin - bonus_promo

                if score < meilleur_score:
                    meilleur_score = score
                    meilleure_offre = offre

            if not meilleure_offre:
                continue

            magasin = db.query(Magasin).filter(
                Magasin.id_magasin == meilleure_offre.id_magasin
            ).first()

            sous_total = meilleure_offre.prix_offre * item.quantite

            # 🚨 budget check
            if total + sous_total > data.budget:
                raise HTTPException(
                    status_code=400,
                    detail="Budget dépassé en scénario équilibré"
                )

            total += sous_total

            # ⚠️ classique = pire prix
            pire_offre = max(
                offres_disponibles,
                key=lambda o: o.prix_offre
            )
            total_classique += pire_offre.prix_offre * item.quantite

            magasins_utilises.add(magasin.nom_magasin)

            if magasin.nom_magasin not in repartition:
                repartition[magasin.nom_magasin] = {
                    "produits": [],
                    "sous_total_magasin": 0
                }

            repartition[magasin.nom_magasin]["produits"].append(
                ProduitOptimiseResponse(
                    id_produit=produit.id_produit,
                    nom=produit.nom_produit,
                    quantite=item.quantite,
                    prix_unitaire=meilleure_offre.prix_offre,
                    sous_total=sous_total
                )
            )

            repartition[magasin.nom_magasin]["sous_total_magasin"] += sous_total

        repartition_list = [
            RepartitionMagasinResponse(
                magasin=nom,
                produits=data_magasin["produits"],
                sous_total_magasin=round(data_magasin["sous_total_magasin"], 2)
            )
            for nom, data_magasin in repartition.items()
        ]

        return OptimisationResponse(
            total=round(total, 2),
            economies=round(total_classique - total, 2),
            repartition=repartition_list
        )

        
    # =========================
    # ⭐ SCENARIO QUALITE
    # =========================
    elif data.scenario == "qualite":

        repartition = {}
        total = 0
        total_classique = 0

        for item in data.produits:

            produit = db.query(Produit).filter(
                Produit.id_produit == item.id_produit
            ).first()

            if not produit:
                raise HTTPException(
                    status_code=404,
                    detail=f"Produit {item.id_produit} introuvable"
                )

            offres = db.query(Offre).filter(
                Offre.id_produit == produit.id_produit
            ).all()

            if not offres:
                continue

            # 🔥 filtrer stock
            offres_disponibles = [
                o for o in offres if o.stock >= item.quantite
            ]

            if not offres_disponibles:
                continue

            # ⭐ priorité aux magasins préférés
            offres_preferes = [
                o for o in offres_disponibles
                if o.id_magasin in data.magasins_preferes
            ]

            # 👉 si dispo dans préférés → on prend le moins cher parmi eux
            if offres_preferes:
                meilleure_offre = min(
                    offres_preferes,
                    key=lambda o: o.prix_offre
                )
            else:
                # fallback → moins cher global
                meilleure_offre = min(
                    offres_disponibles,
                    key=lambda o: o.prix_offre
                )

            # ⚠️ pire prix pour économie
            pire_offre = max(
                offres_disponibles,
                key=lambda o: o.prix_offre
            )

            magasin = db.query(Magasin).filter(
                Magasin.id_magasin == meilleure_offre.id_magasin
            ).first()

            sous_total = meilleure_offre.prix_offre * item.quantite
            sous_total_classique = pire_offre.prix_offre * item.quantite

            # 🚨 budget check
            if total + sous_total > data.budget:
                raise HTTPException(
                    status_code=400,
                    detail="Budget dépassé en scénario qualité"
                )

            total += sous_total
            total_classique += sous_total_classique

            if magasin.nom_magasin not in repartition:
                repartition[magasin.nom_magasin] = {
                    "produits": [],
                    "sous_total_magasin": 0
                }

            repartition[magasin.nom_magasin]["produits"].append(
                ProduitOptimiseResponse(
                    id_produit=produit.id_produit,
                    nom=produit.nom_produit,
                    quantite=item.quantite,
                    prix_unitaire=meilleure_offre.prix_offre,
                    sous_total=sous_total
                )
            )

            repartition[magasin.nom_magasin]["sous_total_magasin"] += sous_total

        repartition_list = [
            RepartitionMagasinResponse(
                magasin=nom,
                produits=data_magasin["produits"],
                sous_total_magasin=round(data_magasin["sous_total_magasin"], 2)
            )
            for nom, data_magasin in repartition.items()
        ]

        return OptimisationResponse(
            total=round(total, 2),
            economies=round(total_classique - total, 2),
            repartition=repartition_list
        )
        # =========================
    # 💸 SCENARIO BUDGET STRICT
    # =========================
    elif data.scenario == "budget_strict":

        repartition = {}
        total = 0

        produits_tries = []

        # 🔥 Trier produits par prix minimum
        for item in data.produits:

            offres = db.query(Offre).filter(
                Offre.id_produit == item.id_produit,
                Offre.stock >= item.quantite
            ).all()

            if not offres:
                continue

            meilleure_offre = min(
                offres,
                key=lambda o: o.prix_offre
            )

            produits_tries.append({
                "item": item,
                "offre": meilleure_offre,
                "prix": meilleure_offre.prix_offre
            })

        produits_tries.sort(key=lambda x: x["prix"] * x["item"].quantite)

        produits_acceptes = []

        for p in produits_tries:

            sous_total = p["prix"] * p["item"].quantite

            if total + sous_total <= data.budget:
                total += sous_total
                produits_acceptes.append(p)

        if not produits_acceptes:
            raise HTTPException(
                status_code=400,
                detail="Budget insuffisant"
            )

        for p in produits_acceptes:

            produit = db.query(Produit).filter(
                Produit.id_produit == p["item"].id_produit
            ).first()

            magasin = db.query(Magasin).filter(
                Magasin.id_magasin == p["offre"].id_magasin
            ).first()

            sous_total = p["offre"].prix_offre * p["item"].quantite

            if magasin.nom_magasin not in repartition:
                repartition[magasin.nom_magasin] = {
                    "produits": [],
                    "sous_total_magasin": 0
                }

            repartition[magasin.nom_magasin]["produits"].append(
                ProduitOptimiseResponse(
                    id_produit=produit.id_produit,
                    nom=produit.nom_produit,
                    quantite=p["item"].quantite,
                    prix_unitaire=p["offre"].prix_offre,
                    sous_total=sous_total
                )
            )

            repartition[magasin.nom_magasin]["sous_total_magasin"] += sous_total

        repartition_list = [
            RepartitionMagasinResponse(
                magasin=nom,
                produits=data_magasin["produits"],
                sous_total_magasin=round(
                    data_magasin["sous_total_magasin"], 2
                )
            )
            for nom, data_magasin in repartition.items()
        ]

        return OptimisationResponse(
            total=round(total, 2),
            economies=0,
            repartition=repartition_list
        )
    
        # =========================
    # ⭐ SCENARIO RECOMMANDE
    # =========================
    elif data.scenario == "recommande":

        repartition = {}
        total = 0

        for item in data.produits:

            produit = db.query(Produit).filter(
                Produit.id_produit == item.id_produit
            ).first()

            if not produit:
                continue

            offres = db.query(Offre).filter(
                Offre.id_produit == item.id_produit,
                Offre.stock >= item.quantite
            ).all()

            if not offres:
                continue

            meilleure_offre = None
            meilleur_score = -1

            for offre in offres:

                score = (
                    produit.qualite_score / max(offre.prix_offre, 0.1)
                )

                if score > meilleur_score:
                    meilleur_score = score
                    meilleure_offre = offre

            magasin = meilleure_offre.magasin

            sous_total = meilleure_offre.prix_offre * item.quantite

            if total + sous_total > data.budget:
                continue

            total += sous_total

            alternative = None

            if meilleure_offre.prix_offre > 50:

                alternative = trouver_alternative(
                    db,
                    produit,
                    meilleure_offre.prix_offre
                )

            if magasin.nom_magasin not in repartition:
                repartition[magasin.nom_magasin] = {
                    "produits": [],
                    "sous_total_magasin": 0
                }

            repartition[magasin.nom_magasin]["produits"].append(
                ProduitOptimiseResponse(
                    id_produit=produit.id_produit,
                    nom=f"{produit.nom_produit} ({produit.marque})",
                    quantite=item.quantite,
                    prix_unitaire=meilleure_offre.prix_offre,
                    sous_total=sous_total
                )
            )

            repartition[magasin.nom_magasin]["sous_total_magasin"] += sous_total

        repartition_list = [
            RepartitionMagasinResponse(
                magasin=nom,
                produits=data_magasin["produits"],
                sous_total_magasin=round(
                    data_magasin["sous_total_magasin"], 2
                )
            )
            for nom, data_magasin in repartition.items()
        ]

        return OptimisationResponse(
            total=round(total, 2),
            economies=0,
            repartition=repartition_list
        )