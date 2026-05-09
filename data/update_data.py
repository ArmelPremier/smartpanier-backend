from random import uniform
from datetime import datetime

from app.database import SessionLocal
from app.models import Offre, HistoriquePrix

db = SessionLocal()

offres = db.query(Offre).all()

for offre in offres:

    ancien_prix = offre.prix_offre

    # 🔥 sauvegarder ancien prix
    historique = HistoriquePrix(
        id_offre=offre.id_offre,
        prix=ancien_prix,
        date=datetime.utcnow()
    )

    db.add(historique)

    # 🔥 variation légère [-2 ; +2]
    variation = uniform(-2, 2)

    nouveau_prix = max(
        1,
        round(ancien_prix + variation, 2)
    )

    # 🔥 update prix
    offre.prix_offre = nouveau_prix

    print(f"{offre.id_offre} : {ancien_prix} -> {nouveau_prix}")

db.commit()
db.close()

print("✅ Mise à jour terminée")