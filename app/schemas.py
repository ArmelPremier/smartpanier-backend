from pydantic import BaseModel

class ProduitCreate(BaseModel):
    nom: str
    categorie: str

class ProduitOut(BaseModel):
    id_produit: int
    nom_produit: str
    categorie_produit: str

    class Config:
        orm_mode = True