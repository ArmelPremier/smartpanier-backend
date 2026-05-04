from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


# 👤 UTILISATEUR
class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id_utilisateur = Column(Integer, primary_key=True, index=True)
    nom_utilisateur = Column(String, nullable=False)
    email_utilisateur = Column(String, unique=True, index=True, nullable=False)
    motdepasse_utilisateur = Column(String, nullable=False)

    listes = relationship("ListeCourses", back_populates="utilisateur")


# 🛒 LISTE COURSES
class ListeCourses(Base):
    __tablename__ = "listecourses"

    id_listecourses = Column(Integer, primary_key=True, index=True)
    budget = Column(Float, nullable=False)
    date_creation = Column(DateTime, default=datetime.utcnow)

    id_utilisateur = Column(Integer, ForeignKey("utilisateurs.id_utilisateur"))

    utilisateur = relationship("Utilisateur", back_populates="listes")
    lignes = relationship("LigneListeCourses", back_populates="liste")
    panier = relationship("PanierOptimise", back_populates="liste", uselist=False)


# 🧩 LIGNE LISTE COURSES
class LigneListeCourses(Base):
    __tablename__ = "ligne_listecourses"

    id_ligne = Column(Integer, primary_key=True, index=True)
    quantite = Column(Integer, nullable=False)

    id_produit = Column(Integer, ForeignKey("produits.id_produit"))
    id_listecourses = Column(Integer, ForeignKey("listecourses.id_listecourses"))

    produit = relationship("Produit")
    liste = relationship("ListeCourses", back_populates="lignes")


# 📦 PRODUIT
class Produit(Base):
    __tablename__ = "produits"

    id_produit = Column(Integer, primary_key=True, index=True)
    nom_produit = Column(String, nullable=False)
    categorie_produit = Column(String, nullable=False)

    offres = relationship("Offre", back_populates="produit")


# 🏪 MAGASIN (ENSEIGNE)
class Magasin(Base):
    __tablename__ = "magasins"

    id_magasin = Column(Integer, primary_key=True, index=True)
    nom_magasin = Column(String, nullable=False)

    offres = relationship("Offre", back_populates="magasin")




# 💰 OFFRE
class Offre(Base):
    __tablename__ = "offres"

    id_offre = Column(Integer, primary_key=True, index=True)
    prix_offre = Column(Float, nullable=False)
    promotion = Column(Boolean, default=False)

    stock = Column(Integer, default=0)

    quantite = Column(String, nullable=False)  # ex: "1kg", "500g", "Pack 6"

    id_produit = Column(Integer, ForeignKey("produits.id_produit"))
    id_magasin = Column(Integer, ForeignKey("magasins.id_magasin"))

    produit = relationship("Produit", back_populates="offres")
    magasin = relationship("Magasin", back_populates="offres")


# 🧠 PANIER OPTIMISÉ
class PanierOptimise(Base):
    __tablename__ = "panieroptimise"

    id_panieroptimise = Column(Integer, primary_key=True, index=True)
    total_panieroptimise = Column(Float, nullable=False)
    economie = Column(Float, nullable=False)

    id_listecourses = Column(Integer, ForeignKey("listecourses.id_listecourses"))

    liste = relationship("ListeCourses", back_populates="panier")
    items = relationship("PanierOptimiseItem", back_populates="panier")

class PanierOptimiseItem(Base):
    __tablename__ = "panier_optimise_items"

    id_item = Column(Integer, primary_key=True, index=True)

    id_panieroptimise = Column(Integer, ForeignKey("panieroptimise.id_panieroptimise"))
    id_produit = Column(Integer, ForeignKey("produits.id_produit"))
    id_magasin = Column(Integer, ForeignKey("magasins.id_magasin"))

    prix_choisi = Column(Float, nullable=False)
    quantite = Column(Integer, nullable=False)

    panier = relationship("PanierOptimise", back_populates="items")
    produit = relationship("Produit")
    magasin = relationship("Magasin")