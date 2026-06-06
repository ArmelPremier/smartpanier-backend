import sys
import json
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.database import SessionLocal
from app.models import Produit, Magasin, Offre
from app.scripts.clean_products import process_file

STORE_NAME = "MyMarket"
SCRAPER    = ROOT_DIR / "app/scraper/scraper_mymarket.py"
RAW_JSON   = ROOT_DIR / "app/scraper/mymarket_products.json"
CLEAN_JSON = ROOT_DIR / "data/mymarket_products_clean.json"


def scrape():
    print("Scraping MyMarket...")
    subprocess.run(
        [sys.executable, str(SCRAPER)],
        cwd=str(ROOT_DIR / "app/scraper"),
        check=True
    )
    print("Scraping terminé")


def clean():
    print("Nettoyage des données...")
    process_file(RAW_JSON, CLEAN_JSON)
    print("Nettoyage terminé")


def update_db():
    print("Mise à jour de la base de données...")
    db = SessionLocal()

    try:
        magasin = db.query(Magasin).filter(
            Magasin.nom_magasin == STORE_NAME
        ).first()

        if not magasin:
            magasin = Magasin(nom_magasin=STORE_NAME)
            db.add(magasin)
            db.commit()
            db.refresh(magasin)

        with open(CLEAN_JSON, "r", encoding="utf-8") as f:
            produits_json = json.load(f)

        nb_nouveaux = 0
        nb_maj = 0

        for item in produits_json:

            product_key = item["product_key"]

            produit = db.query(Produit).filter(
                Produit.product_key == product_key
            ).first()

            if not produit:
                produit = Produit(
                    product_key=product_key,
                    nom_produit=item["nom"],
                    categorie_produit=item["categorie_canonique"],
                    marque=item.get("marque"),
                    quantite=item["quantite"],
                    code_normalise=item.get("code_normalise"),
                    qualite_score=item.get("qualite_score", 5)
                )
                db.add(produit)
                db.flush()
                nb_nouveaux += 1

            # Remplacer l'offre existante de ce magasin pour ce produit
            db.query(Offre).filter(
                Offre.id_produit == produit.id_produit,
                Offre.id_magasin == magasin.id_magasin
            ).delete()

            db.add(Offre(
                prix_offre=item["prix"],
                promotion=False,
                stock=100,
                id_produit=produit.id_produit,
                id_magasin=magasin.id_magasin
            ))
            nb_maj += 1

        db.commit()
        print(f"{STORE_NAME} — {nb_nouveaux} nouveaux produits, {nb_maj} offres mises à jour")

    except Exception as e:
        db.rollback()
        print("Erreur :", e)
        raise

    finally:
        db.close()


if __name__ == "__main__":
    scrape()
    clean()
    update_db()
