from fastapi import APIRouter
from app.database import SessionLocal
from app.models import Offre

router = APIRouter()

@router.get("/offres/{produit_id}")
def get_offres(produit_id: int):
    db = SessionLocal()

    offres = db.query(Offre).filter_by(id_produit=produit_id).all()

    return offres