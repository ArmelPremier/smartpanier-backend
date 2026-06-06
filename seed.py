import json

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Produit, Magasin, Offre


def seed_store(json_file, store_name):

    db: Session = SessionLocal()

    try:

        # ============================
        # Magasin
        # ============================

        magasin = (
            db.query(Magasin)
            .filter(
                Magasin.nom_magasin == store_name
            )
            .first()
        )

        if not magasin:

            magasin = Magasin(
                nom_magasin=store_name
            )

            db.add(magasin)
            db.commit()
            db.refresh(magasin)

        # ============================
        # JSON
        # ============================

        with open(
            json_file,
            "r",
            encoding="utf-8"
        ) as f:

            produits_json = json.load(f)

        nb_produits = 0
        nb_offres = 0

        # ====================================
        # Produits + Offres
        # ====================================

        for item in produits_json:

            product_key = item["product_key"]

            produit = (
                db.query(Produit)
                .filter(
                    Produit.product_key == product_key
                )
                .first()
            )

            if not produit:

                produit = Produit(

                    product_key=product_key,

                    nom_produit=item["nom"],

                    categorie_produit=item[
                        "categorie_canonique"
                    ],

                    marque=item.get("marque"),

                    quantite=item["quantite"],

                    code_normalise=item.get(
                        "code_normalise"
                    ),

                    qualite_score=item.get(
                        "qualite_score",
                        5
                    )
                )

                db.add(produit)
                db.flush()

                nb_produits += 1
            # ----------------------------
            # Offre
            # ----------------------------

            offre = Offre(
                prix_offre=item["prix"],
                promotion=False,
                stock=100,
                id_produit=produit.id_produit,
                id_magasin=magasin.id_magasin
            )

            db.add(offre)
            nb_offres += 1

        db.commit()

        print(f"\n[OK] {store_name}")
        print(f"Produits crees : {nb_produits}")
        print(f"Offres creees : {nb_offres}")

    except Exception as e:

        db.rollback()
        print("[ERREUR] :", e)

    finally:
        db.close()


if __name__ == "__main__":

    seed_store(
        "data/mymarket_products_clean.json",
        "MyMarket"
    )

    seed_store(
        "data/marketpro_products_clean.json",
        "MarketPro"
    )