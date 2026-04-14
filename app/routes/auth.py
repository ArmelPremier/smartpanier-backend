from fastapi import APIRouter, HTTPException
from app.database import SessionLocal
from app.models import Utilisateur
from app.utils.security import create_token

router = APIRouter()

@router.post("/register")
def register(nom: str, email: str, password: str):
    db = SessionLocal()

    user = Utilisateur(
        nom_utilisateur=nom,
        email_utilisateur=email,
        motdepasse_utilisateur=password
    )

    db.add(user)
    db.commit()

    return {"message": "Utilisateur créé"}

@router.post("/login")
def login(email: str, password: str):
    db = SessionLocal()

    user = db.query(Utilisateur).filter_by(email_utilisateur=email).first()

    if not user or user.motdepasse_utilisateur != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token({"sub": user.email_utilisateur})

    return {"access_token": token}