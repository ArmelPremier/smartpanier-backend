from app.database import engine

try:
    conn = engine.connect()
    print("✅ Supabase connecté avec succès !")
    conn.close()
except Exception as e:
    print("❌ Erreur connexion :", e)