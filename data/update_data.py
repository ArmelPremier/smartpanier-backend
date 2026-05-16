from datetime import datetime

from app.database import SessionLocal
from app.models import Offre, HistoriquePrix

db = SessionLocal()

# 🔥 afficher toutes les offres
offres = db.query(Offre).all()

print("\n===== LISTE DES OFFRES =====\n")

for offre in offres:
    print(
        f"ID Offre: {offre.id_offre} | "
        f"Produit ID: {offre.id_produit} | "
        f"Magasin ID: {offre.id_magasin} | "
        f"Prix actuel: {offre.prix_offre} DH"
    )

print("\n============================\n")

# 🔥 choisir offre
id_offre = int(input("Entrer l'ID de l'offre à modifier : "))

offre = db.query(Offre).filter(
    Offre.id_offre == id_offre
).first()

if not offre:
    print("❌ Offre introuvable")
    db.close()
    exit()

ancien_prix = offre.prix_offre

print(f"\nPrix actuel : {ancien_prix} DH")

# 🔥 nouveau prix
nouveau_prix = float(
    input("Entrer le nouveau prix : ")
)

# 🔥 sécurité simple
if nouveau_prix <= 0:
    print("❌ Prix invalide")
    db.close()
    exit()

# 🔥 sauvegarder historique
historique = HistoriquePrix(
    id_offre=offre.id_offre,
    prix=ancien_prix,
    date=datetime.utcnow()
)

db.add(historique)

# 🔥 mise à jour prix
offre.prix_offre = round(nouveau_prix, 2)

db.commit()

print(
    f"\n✅ Offre {offre.id_offre} mise à jour : "
    f"{ancien_prix} DH -> {nouveau_prix} DH"
)

db.close()