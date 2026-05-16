from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.utils.security import hash_password

from app.database import get_db
from app.models import *
from app.schemas import UserRegister, UserLogin, ChangePasswordRequest
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
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    db_user = db.query(Utilisateur).filter(
        Utilisateur.email_utilisateur == form_data.username
    ).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Email incorrect")

    if not verify_password(
        form_data.password,
        db_user.motdepasse_utilisateur
    ):
        raise HTTPException(status_code=401, detail="Mot de passe incorrect")

    token = create_token({
        "sub": db_user.email_utilisateur
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }
# =========================
# 🔐 CHANGE PASSWORD
# =========================
@router.put("/change-password")
def change_password(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db)
):

    user = db.query(Utilisateur).filter(
        Utilisateur.email_utilisateur == data.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Utilisateur introuvable"
        )

    # 🔥 vérifier ancien mot de passe
    if not verify_password(
        data.ancien_motdepasse,
        user.motdepasse_utilisateur
    ):
        raise HTTPException(
            status_code=401,
            detail="Ancien mot de passe incorrect"
        )

    # 🔥 nouveau hash
    user.motdepasse_utilisateur = hash_password(
        data.nouveau_motdepasse
    )

    db.commit()

    return {
        "message": "Mot de passe modifié avec succès"
    }