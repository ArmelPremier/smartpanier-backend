from app.database import engine, Base

# 🔥 importer les modèles
import app.models

# 🔥 créer les tables
Base.metadata.create_all(bind=engine)

print("✅ Tables créées avec succès")