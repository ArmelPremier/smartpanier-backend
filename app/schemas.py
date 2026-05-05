from pydantic import BaseModel
from typing import List, Optional


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

class Offre(BaseModel):
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

class ScenarioResponse(BaseModel):
    code: str
    nom: str
    description: str

# =====================================================
# 🧠 NOUVEAU FLUX SMARTPANIER → POST /optimiser
# =====================================================

# ---------- INPUT ----------

class OptimisationProduitInput(BaseModel):
    id_produit: int
    quantite: int


class OptimisationRequest(BaseModel):
    budget: float
    scenario: str
    produits: List[OptimisationProduitInput]

    magasins_preferes: list[int] = []  # ex: [1, 2]


# ---------- OUTPUT ----------

class ProduitOptimiseResponse(BaseModel):
    id_produit: int
    nom: str
    quantite: int
    prix_unitaire: float
    sous_total: float


class RepartitionMagasinResponse(BaseModel):
    magasin: str
    produits: List[ProduitOptimiseResponse]
    sous_total_magasin: float


class OptimisationResponse(BaseModel):
    total: float
    economies: float
    repartition: List[RepartitionMagasinResponse]


# =========================
# (ancien panier - optionnel)
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