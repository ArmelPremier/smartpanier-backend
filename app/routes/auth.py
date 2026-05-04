from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.utils.security import hash_password

from app.database import get_db
from app.models import *
from app.schemas import UserRegister, UserLogin
from app.utils.security import create_token
from app.utils.security import verify_password

router = APIRouter(prefix="", tags=["Auth"])


# =========================
# 🔐 REGISTER
# =========================
@router.post("/register")
def register(user: UserRegister, db: Session = Depends(get_db)):

    # 🔎 vérifier si utilisateur existe déjà
    existing = db.query(Utilisateur).filter(
        Utilisateur.email_utilisateur == user.email
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    new_user = Utilisateur(
        nom_utilisateur=user.nom,
        email_utilisateur=user.email,
        motdepasse_utilisateur=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()

    return {"message": "Utilisateur créé"}


# =========================
# 🔐 LOGIN
# =========================
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):

    db_user = db.query(Utilisateur).filter(
        Utilisateur.email_utilisateur == user.email
    ).first()

    if not db_user or not verify_password(user.password, db_user.motdepasse_utilisateur):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token({"sub": db_user.email_utilisateur})

    return {"access_token": token}

@router.post("/logout")
def logout():
    return {"message": "Déconnexion réussie"}