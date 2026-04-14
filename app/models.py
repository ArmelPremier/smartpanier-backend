from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from app.database import Base

class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id_utilisateur = Column(Integer, primary_key=True)
    nom_utilisateur = Column(String)
    email_utilisateur = Column(String, unique=True)
    motdepasse_utilisateur = Column(String)


class Produit(Base):
    __tablename__ = "produits"

    id_produit = Column(Integer, primary_key=True)
    nom_produit = Column(String)
    categorie_produit = Column(String)


class Magasin(Base):
    __tablename__ = "magasins"

    id_magasin = Column(Integer, primary_key=True)
    nom_magasin = Column(String)
    localisation_magasin = Column(String)


class Offre(Base):
    __tablename__ = "offres"

    id_offre = Column(Integer, primary_key=True)
    prix_offre = Column(Float)
    promotion = Column(Boolean)

    id_produit = Column(Integer, ForeignKey("produits.id_produit"))
    id_magasin = Column(Integer, ForeignKey("magasins.id_magasin"))