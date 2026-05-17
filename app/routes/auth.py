from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Utilisateur
from app.schemas import (
    UserRegister,
    UserLogin,
    ChangePasswordRequest
)

from app.utils.security import (
    hash_password,
    verify_password,
    create_token
)

router = APIRouter(
    prefix="",
    tags=["Auth"]
)


# =========================
# 🔐 REGISTER
# =========================
@router.post("/register")
def register(
    user: UserRegister,
    db: Session = Depends(get_db)
):

    # 🔎 Vérifier si email déjà utilisé
    existing_user = db.query(Utilisateur).filter(
        Utilisateur.email_utilisateur == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email déjà utilisé"
        )

    # 🔥 Création utilisateur
    new_user = Utilisateur(
        nom_utilisateur=user.nom,
        email_utilisateur=user.email,
        motdepasse_utilisateur=hash_password(
            user.password
        )
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Utilisateur créé avec succès",
        "user": {
            "id": new_user.id_utilisateur,
            "nom": new_user.nom_utilisateur,
            "email": new_user.email_utilisateur
        }
    }


# =========================
# 🔐 LOGIN
# =========================
@router.post("/login")
def login(
    user: UserLogin,
    db: Session = Depends(get_db)
):

    # 🔎 Recherche utilisateur via email
    db_user = db.query(Utilisateur).filter(
        Utilisateur.email_utilisateur == user.email
    ).first()

    # ❌ Email incorrect
    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Email incorrect"
        )

    # ❌ Mot de passe incorrect
    if not verify_password(
        user.password,
        db_user.motdepasse_utilisateur
    ):
        raise HTTPException(
            status_code=401,
            detail="Mot de passe incorrect"
        )

    # 🔥 Génération JWT
    token = create_token({
        "sub": db_user.email_utilisateur
    })

    # ✅ Retour compatible frontend
    return {
        "message": "Connexion réussie",
        "access_token": token,
        "token_type": "bearer",

        "user": {
            "id": db_user.id_utilisateur,
            "nom": db_user.nom_utilisateur,
            "email": db_user.email_utilisateur
        }
    }


# =========================
# 🔐 CHANGE PASSWORD
# =========================
@router.put("/change-password")
def change_password(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db)
):

    # 🔎 Vérifier utilisateur
    user = db.query(Utilisateur).filter(
        Utilisateur.email_utilisateur == data.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Utilisateur introuvable"
        )

    # 🔎 Vérifier ancien mot de passe
    if not verify_password(
        data.ancien_motdepasse,
        user.motdepasse_utilisateur
    ):
        raise HTTPException(
            status_code=401,
            detail="Ancien mot de passe incorrect"
        )

    # 🔥 Hash nouveau mot de passe
    user.motdepasse_utilisateur = hash_password(
        data.nouveau_motdepasse
    )

    db.commit()

    return {
        "message": "Mot de passe modifié avec succès"
    }