from app.models import Produit, Offre


def trouver_alternative(db, produit, budget_max=None):

    alternatives = db.query(Produit).filter(
        Produit.categorie_produit == produit.categorie_produit,
        Produit.id_produit != produit.id_produit
    ).all()

    meilleure_alternative = None
    meilleur_prix = float("inf")

    for alt in alternatives:

        offres = db.query(Offre).filter(
            Offre.id_produit == alt.id_produit,
            Offre.stock > 0
        ).all()

        if not offres:
            continue

        offre_moins_chere = min(
            offres,
            key=lambda o: o.prix_offre
        )

        prix = offre_moins_chere.prix_offre

        if budget_max and prix > budget_max:
            continue

        if prix < meilleur_prix:
            meilleur_prix = prix
            meilleure_alternative = {
                "id_produit": alt.id_produit,
                "nom": alt.nom_produit,
                "marque": alt.marque,
                "prix": prix
            }

    return meilleure_alternative