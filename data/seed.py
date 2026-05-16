from app.database import SessionLocal
from app.models import Produit, Offre, Magasin, HistoriquePrix
from data.fake_data import produits, offres, magasins

db = SessionLocal()

# =========================
# 🔥 RESET TABLES
# =========================
db.query(HistoriquePrix).delete()
db.query(Offre).delete()
db.query(Produit).delete()
db.query(Magasin).delete()

db.commit()

# =========================
# 🏪 MAGASINS
# =========================
for m in magasins:

    magasin = Magasin(
        id_magasin=m["id"],
        nom_magasin=m["nom"]
    )

    db.add(magasin)

db.commit()

# =========================
# 📦 PRODUITS
# =========================
for p in produits:

    produit = Produit(
        nom_produit=p["nom"],
        categorie_produit=p["categorie"],
        marque=p["marque"],
        qualite_score=p["qualite_score"]
    )

    db.add(produit)

db.commit()

# =========================
# 💰 OFFRES
# =========================
for o in offres:

    offre = Offre(
        id_produit=o["id_produit"],
        id_magasin=o["id_magasin"],
        prix_offre=o["prix_offre"],
        promotion=o["promotion"],
        stock=o["stock"],
        quantite=o["quantite"]
    )

    db.add(offre)

db.commit()

# =========================
# 📈 HISTORIQUE PRIX INITIAL
# =========================
all_offres = db.query(Offre).all()

for offre in all_offres:

    historique = HistoriquePrix(
        id_offre=offre.id_offre,
        prix=offre.prix_offre
    )

    db.add(historique)

db.commit()
db.close()

print("✅ Seed terminé avec succès")