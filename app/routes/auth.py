from fastapi import APIRouter, HTTPException, Depends

from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Utilisateur
from app.config import SECRET_KEY, ALGORITHM


from app.schemas import (
    UserRegister,
    UserLogin,
    ChangePasswordRequest,
    RefreshRequest
)

from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_current_user,
    verify_refresh_token
)

router = APIRouter(tags=["Auth"])




# =========================
# 🔐 REGISTER
# =========================

@router.post("/register", summary="Créer un compte utilisateur")
def register(user: UserRegister, db: Session = Depends(get_db)):

    existing_user = db.query(Utilisateur).filter(
        Utilisateur.email_utilisateur == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email déjà utilisé"
        )

    new_user = Utilisateur(
        nom_utilisateur=user.nom.strip(),
        email_utilisateur=user.email.lower().strip(),
        motdepasse_utilisateur=hash_password(user.password)
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

@router.post("/login", summary="Se connecter et obtenir un token JWT")
def login(user: UserLogin, db: Session = Depends(get_db)):

    db_user = db.query(Utilisateur).filter(
        Utilisateur.email_utilisateur == user.email
    ).first()

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Email incorrect"
        )

    if not verify_password(user.password, db_user.motdepasse_utilisateur):
        raise HTTPException(
            status_code=401,
            detail="Mot de passe incorrect"
        )

    access_token = create_access_token({
        "sub": db_user.email_utilisateur
    })

    refresh_token = create_refresh_token({
        "sub": db_user.email_utilisateur
    })

    return {
        "message": "Connexion réussie",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": db_user.id_utilisateur,
            "nom": db_user.nom_utilisateur,
            "email": db_user.email_utilisateur
        }
    }


# =========================
# 👤 CURRENT USER
# =========================

@router.get("/me", summary="Profil de l'utilisateur connecté")
def get_me(current_user=Depends(get_current_user)):

    return {
        "id": current_user.id_utilisateur,
        "nom": current_user.nom_utilisateur,
        "email": current_user.email_utilisateur
    }


# =========================
# 🔐 CHANGE PASSWORD
# =========================

@router.put("/change-password", summary="Modifier le mot de passe")
def change_password(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    if current_user.email_utilisateur != data.email:
        raise HTTPException(
            status_code=403,
            detail="Action non autorisée"
        )

    if not verify_password(
        data.ancien_motdepasse,
        current_user.motdepasse_utilisateur
    ):
        raise HTTPException(
            status_code=401,
            detail="Ancien mot de passe incorrect"
        )

    current_user.motdepasse_utilisateur = hash_password(
        data.nouveau_motdepasse
    )

    db.commit()

    return {
        "message": "Mot de passe modifié avec succès"
    }


# =========================
# 🔄 REFRESH TOKEN
# =========================

@router.post("/refresh", summary="Rafraîchir le token d'accès")
def refresh_access_token(data: RefreshRequest):
    payload = verify_refresh_token(data.refresh_token)

    email = payload.get("sub")

    new_access_token = create_access_token({
        "sub": email
    })

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }