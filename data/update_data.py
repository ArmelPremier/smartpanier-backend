import random
from app.database import SessionLocal
from app.models import Offre

def update_offres():
    db = SessionLocal()

    offres = db.query(Offre).all()

    for offre in offres:
        # 🔄 Variation prix (-10% à +10%)
        variation = random.uniform(-0.1, 0.1)
        offre.prix_offre = round(offre.prix_offre * (1 + variation), 2)

        # 📦 Stock aléatoire
        offre.stock = random.randint(0, 100)

        # 🎯 Promo aléatoire
        offre.promotion = random.choice([True, False])

    db.commit()
    db.close()

    print("✅ Données mises à jour avec succès")

if __name__ == "__main__":
    update_offres()