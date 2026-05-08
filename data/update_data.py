from random import uniform
from app.database import SessionLocal
from app.models import Offre, HistoriquePrix

db = SessionLocal()

offres = db.query(Offre).all()

for offre in offres:

    ancien_prix = offre.prix_offre

    variation = uniform(-2, 2)

    nouveau_prix = max(1, round(ancien_prix + variation, 2))

    offre.prix_offre = nouveau_prix

    historique = HistoriquePrix(
        id_offre=offre.id_offre,
        prix=nouveau_prix
    )

    db.add(historique)

    print(f"{offre.id_offre} : {ancien_prix} -> {nouveau_prix}")

db.commit()
db.close()

print("✅ Mise à jour terminée")