from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


# 👤 UTILISATEUR
class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id_utilisateur = Column(Integer, primary_key=True)
    nom_utilisateur = Column(String)
    email_utilisateur = Column(String, unique=True)
    motdepasse_utilisateur = Column(String)

    listes = relationship("ListeCourses", back_populates="utilisateur")


# 🛒 LISTE COURSES
class ListeCourses(Base):
    __tablename__ = "listecourses"

    id_listecourses = Column(Integer, primary_key=True)
    budget = Column(Float)
    date_creation = Column(DateTime)

    id_utilisateur = Column(Integer, ForeignKey("utilisateurs.id_utilisateur"))

    utilisateur = relationship("Utilisateur", back_populates="listes")
    lignes = relationship("LigneListeCourses", back_populates="liste")
    panier = relationship("PanierOptimise", back_populates="liste", uselist=False)


# 🧩 LIGNE LISTE COURSES
class LigneListeCourses(Base):
    __tablename__ = "ligne_listecourses"

    id_ligne = Column(Integer, primary_key=True)
    quantite = Column(Integer)

    id_produit = Column(Integer, ForeignKey("produits.id_produit"))
    id_listecourses = Column(Integer, ForeignKey("listecourses.id_listecourses"))

    produit = relationship("Produit")
    liste = relationship("ListeCourses", back_populates="lignes")


# 📦 PRODUIT
class Produit(Base):
    __tablename__ = "produits"

    id_produit = Column(Integer, primary_key=True)
    nom_produit = Column(String)
    categorie_produit = Column(String)

    offres = relationship("Offre", back_populates="produit")


# 🏪 MAGASIN
class Magasin(Base):
    __tablename__ = "magasins"

    id_magasin = Column(Integer, primary_key=True)
    nom_magasin = Column(String)
    localisation_magasin = Column(String)

    offres = relationship("Offre", back_populates="magasin")


# 💰 OFFRE
class Offre(Base):
    __tablename__ = "offres"

    id_offre = Column(Integer, primary_key=True)
    prix_offre = Column(Float)
    promotion = Column(Boolean)

    id_produit = Column(Integer, ForeignKey("produits.id_produit"))
    id_magasin = Column(Integer, ForeignKey("magasins.id_magasin"))

    produit = relationship("Produit", back_populates="offres")
    magasin = relationship("Magasin", back_populates="offres")


# 🧠 PANIER OPTIMISÉ
class PanierOptimise(Base):
    __tablename__ = "panieroptimise"

    id_panieroptimise = Column(Integer, primary_key=True)
    total_panieroptimise = Column(Float)
    economie = Column(Float)

    id_listecourses = Column(Integer, ForeignKey("listecourses.id_listecourses"))

    liste = relationship("ListeCourses", back_populates="panier")