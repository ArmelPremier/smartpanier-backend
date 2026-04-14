from fastapi import FastAPI
from app.database import engine, Base

app = FastAPI()

# créer tables au démarrage
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"message": "API + Supabase OK"}