from app.models import Produit, Offre


def trouver_alternatives(db, produit, budget_max=None, limit=3):

    alternatives = db.query(Produit).filter(
        Produit.categorie_produit == produit.categorie_produit,
        Produit.id_produit != produit.id_produit
    ).all()

    resultats = []

    for alt in alternatives:

        offres = db.query(Offre).filter(
            Offre.id_produit == alt.id_produit,
            Offre.stock > 0
        ).all()

        if not offres:
            continue

        offre_moins_chere = min(offres, key=lambda o: o.prix_offre)
        prix = offre_moins_chere.prix_offre

        if budget_max and prix > budget_max:
            continue

        resultats.append({
            "id_produit": alt.id_produit,
            "nom": alt.nom_produit,
            "marque": alt.marque,
            "prix": prix
        })

    resultats.sort(key=lambda x: x["prix"])
    return resultats[:limit]
