from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# =========================
# 👤 AUTH
# =========================

class UserRegister(BaseModel):
    nom: str = Field(..., description="Nom complet de l'utilisateur")
    email: str = Field(..., description="Adresse email unique")
    password: str = Field(..., description="Mot de passe (min. 6 caractères)")


class UserLogin(BaseModel):
    email: str = Field(..., description="Adresse email")
    password: str = Field(..., description="Mot de passe")


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
# 🔁 ALTERNATIVE PRODUIT
# =========================

class AlternativeProduitResponse(BaseModel):
    id_produit: int
    nom: str
    marque: Optional[str] = None
    prix: float


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
    id_produit: int = Field(..., description="ID du produit")
    quantite: float = Field(..., description="Quantité souhaitée")
    unite: Optional[str] = Field(None, description="Unité (ex: '1kg', '500g')")


class OptimisationRequest(BaseModel):
    id_liste: int = Field(..., description="ID de la liste de courses")
    budget: float = Field(..., description="Budget maximum en MAD")
    scenario: str = Field(
        ...,
        description="Scénario : 'prix_min' | 'mono_2_magasins' | 'budget_strict' | 'recommande'"
    )
    produits: List[OptimisationProduitInput] = Field(..., description="Produits à optimiser")
    magasins_preferes: List[int] = Field([], description="IDs des magasins préférés (optionnel)")


# ---------- OUTPUT ----------

class ProduitOptimiseResponse(BaseModel):
    id_produit: int
    nom: str

    marque: Optional[str] = None
    qualite_score: Optional[float] = None

    quantite: int
    prix_unitaire: float
    sous_total: float
    unite: Optional[str] = None
    quantite_normalisee: Optional[float] = None

    alternative: Optional[AlternativeProduitResponse] = None


class RepartitionMagasinResponse(BaseModel):
    magasin: str
    produits: List[ProduitOptimiseResponse]
    sous_total_magasin: float




# =========================
# 🛒 PANIER OPTIMISÉ
# =========================

class PanierOptimiseItem(BaseModel):
    produit: str
    magasin: Optional[str] = None

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

# =====================================================
# 🛒 LISTES DE COURSES (NOUVEAU MODULE)
# =====================================================

class LigneListeCreate(BaseModel):
    id_produit: int
    quantite: int


class LigneListeResponse(BaseModel):
    id_ligne: int
    id_produit: int
    quantite: int

    model_config = {
        "from_attributes": True
    }


class ListeCoursesCreate(BaseModel):
    nom_liste: str = Field(..., description="Nom de la liste de courses")
    budget: Optional[float] = Field(None, description="Budget maximum en MAD")
    produits: List[LigneListeCreate] = Field(..., description="Produits initiaux de la liste")


class ListeCoursesResponse(BaseModel):
    id_liste: int
    nom_liste: str
    budget: Optional[float]
    date_creation: datetime
    lignes: List[LigneListeResponse]

    model_config = {
        "from_attributes": True
    }


# =====================================================
# 📜 HISTORIQUE LISTES UTILISATEUR
# =====================================================

class HistoriqueListeResponse(BaseModel):
    id_liste: int
    nom_liste: str
    budget: Optional[float]
    date_creation: datetime
    nombre_produits: int

    model_config = {
        "from_attributes": True
    }

class ListeCoursesUpdate(BaseModel):
    nom_liste: Optional[str] = None
    budget: Optional[float] = None

# =====================================================
# ➕ AJOUT PRODUIT DANS LISTE
# =====================================================

class AddProduitListeRequest(BaseModel):
    id_produit: int
    quantite: int

class OptimisationResponse(BaseModel):
    total: float
    total_initial: float
    economies: float
    repartition: List[RepartitionMagasinResponse]

class RefreshRequest(BaseModel):
    refresh_token: str