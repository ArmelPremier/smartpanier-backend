from pydantic import BaseModel
from typing import List, Optional

from app.utils.security import get_current_user
from app.schemas import OffreResponse


# =========================
# 👤 AUTH
# =========================

class UserRegister(BaseModel):
    nom: str
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


# =========================
# 📦 PRODUIT
# =========================

class ProduitBase(BaseModel):
    nom_produit: str
    categorie_produit: str
    marque: Optional[str] = None
    qualite_score: Optional[float] = 5


class ProduitCreate(ProduitBase):
    pass


class ProduitResponse(ProduitBase):
    id_produit: int

    model_config = {
        "from_attributes": True
    }


# =========================
# 💰 OFFRE
# =========================

class OffreResponse(BaseModel):
    id_offre: int
    prix_offre: float
    promotion: bool
    quantite: str
    stock: int
    id_produit: int
    id_magasin: int

    model_config = {
        "from_attributes": True
    }


# =========================
# 🎯 SCÉNARIOS
# =========================

class ScenarioResponse(BaseModel):
    code: str
    nom: str
    description: str


# =====================================================
# 🧠 SMARTPANIER → POST /optimiser
# =====================================================

# ---------- INPUT ----------

class OptimisationProduitInput(BaseModel):
    id_produit: int
    quantite: int


class OptimisationRequest(BaseModel):
    budget: float
    scenario: str
    produits: List[OptimisationProduitInput]

    magasins_preferes: list[int] = []


# ---------- OUTPUT ----------

class ProduitOptimiseResponse(BaseModel):
    id_produit: int
    nom: str
    marque: Optional[str] = None
    qualite_score: Optional[float] = None

    quantite: int
    prix_unitaire: float
    sous_total: float
    alternative=alternative

    alternative: Optional[AlternativeProduitResponse] = None


class RepartitionMagasinResponse(BaseModel):
    magasin: str
    produits: List[ProduitOptimiseResponse]
    sous_total_magasin: float


class OptimisationResponse(BaseModel):
    total: float
    economies: float
    repartition: List[RepartitionMagasinResponse]


# =========================
# 🛒 PANIER OPTIMISÉ
# =========================

class PanierOptimiseItem(BaseModel):
    produit: str
    magasin: Optional[str]

    prix: float
    quantite: int
    total: float


class PanierOptimiseResponse(BaseModel):
    items: List[PanierOptimiseItem]

    total_optimise: float
    total_classique: float
    economie: float

# =========================
# 🔐 CHANGE PASSWORD
# =========================

class ChangePasswordRequest(BaseModel):
    email: str
    ancien_motdepasse: str
    nouveau_motdepasse: str

class AlternativeProduitResponse(BaseModel):
    id_produit: int
    nom: str
    marque: Optional[str] = None
    prix: float