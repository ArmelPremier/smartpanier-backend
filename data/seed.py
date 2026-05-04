from app.database import SessionLocal
from app.models import Produit, Offre, Magasin
from data.fake_data import produits, offres, magasins

db = SessionLocal()

# 🔥 RESET
db.query(Offre).delete()
db.query(Produit).delete()
db.query(Magasin).delete()
db.commit()

# =========================
# 🏪 MAGASINS
# =========================
for m in magasins:
    db.add(Magasin(
        id_magasin=m["id"],
        nom_magasin=m["nom"]
    ))
db.commit()

# =========================
# 📦 PRODUITS
# =========================
for p in produits:
    db.add(Produit(
        nom_produit=p["nom"],
        categorie_produit=p["categorie"]
    ))
db.commit()

# =========================
# 💰 OFFRES
# =========================
for o in offres:
    db.add(Offre(**o))

db.commit()
db.close()

print("✅ Seed terminé avec succès")