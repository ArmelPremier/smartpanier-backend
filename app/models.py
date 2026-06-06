from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    ForeignKey,
    DateTime
)

from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


# =====================================================
# 👤 UTILISATEUR
# =====================================================

class Utilisateur(Base):

    __tablename__ = "utilisateurs"

    id_utilisateur = Column(
        Integer,
        primary_key=True,
        index=True
    )

    nom_utilisateur = Column(
        String,
        nullable=False
    )

    email_utilisateur = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    motdepasse_utilisateur = Column(
        String,
        nullable=False
    )

    # Relations
    listes = relationship(
        "ListeCourses",
        back_populates="utilisateur",
        cascade="all, delete-orphan"
    )


# =====================================================
# 🛒 LISTE DE COURSES
# =====================================================

class ListeCourses(Base):

    __tablename__ = "listes_courses"

    id_liste = Column(
        Integer,
        primary_key=True,
        index=True
    )

    nom_liste = Column(
        String,
        nullable=False
    )

    budget = Column(
        Float,
        nullable=True
    )

    date_creation = Column(
        DateTime,
        default=datetime.utcnow
    )

    id_utilisateur = Column(
        Integer,
        ForeignKey("utilisateurs.id_utilisateur"),
        nullable=False
    )

    # Relations
    utilisateur = relationship(
        "Utilisateur",
        back_populates="listes"
    )

    lignes = relationship(
        "LigneListeCourses",
        back_populates="liste",
        cascade="all, delete-orphan"
    )

    paniers_optimises = relationship(
    "PanierOptimise",
    back_populates="liste",
    cascade="all, delete-orphan"
)


# =====================================================
# 📦 LIGNES DE LISTE
# =====================================================

class LigneListeCourses(Base):

    __tablename__ = "ligne_liste_courses"

    id_ligne = Column(
        Integer,
        primary_key=True,
        index=True
    )

    quantite = Column(
        Integer,
        nullable=False
    )

    id_produit = Column(
        Integer,
        ForeignKey("produits.id_produit"),
        nullable=False
    )

    id_liste = Column(
        Integer,
        ForeignKey("listes_courses.id_liste"),
        nullable=False
    )

    # Relations
    produit = relationship(
        "Produit",
        back_populates="lignes_liste"
    )

    liste = relationship(
        "ListeCourses",
        back_populates="lignes"
    )


# =====================================================
# 📦 PRODUITS
# =====================================================

class Produit(Base):

    __tablename__ = "produits"

    id_produit = Column(
        Integer,
        primary_key=True,
        index=True
    )

    product_key = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    nom_produit = Column(
        String,
        nullable=False
    )

    categorie_produit = Column(
        String,
        nullable=False
    )

    marque = Column(
        String,
        nullable=True
    )

    quantite = Column(
        String,
        nullable=False
    )

    code_normalise = Column(
        String,
        nullable=True
    )

    qualite_score = Column(
        Float,
        default=5
    )

    # Relations
    offres = relationship(
        "Offre",
        back_populates="produit",
        cascade="all, delete-orphan"
    )

    lignes_liste = relationship(
        "LigneListeCourses",
        back_populates="produit"
    )

    panier_items = relationship(
        "PanierOptimiseItem",
        back_populates="produit"
    )


# =====================================================
# 🏪 MAGASINS
# =====================================================

class Magasin(Base):

    __tablename__ = "magasins"

    id_magasin = Column(
        Integer,
        primary_key=True,
        index=True
    )

    nom_magasin = Column(
        String,
        nullable=False
    )

    # Relations
    offres = relationship(
        "Offre",
        back_populates="magasin",
        cascade="all, delete-orphan"
    )

    panier_items = relationship(
        "PanierOptimiseItem",
        back_populates="magasin"
    )


# =====================================================
# 💰 OFFRES
# =====================================================

class Offre(Base):

    __tablename__ = "offres"

    id_offre = Column(
        Integer,
        primary_key=True,
        index=True
    )

    prix_offre = Column(
        Float,
        nullable=False
    )

    promotion = Column(
        Boolean,
        default=False
    )

    stock = Column(
        Integer,
        default=0
    )


    id_produit = Column(
        Integer,
        ForeignKey("produits.id_produit"),
        nullable=False
    )

    id_magasin = Column(
        Integer,
        ForeignKey("magasins.id_magasin"),
        nullable=False
    )

    date_scraping = Column(
        DateTime,
        default=datetime.utcnow
    )

    # Relations
    produit = relationship(
        "Produit",
        back_populates="offres"
    )

    magasin = relationship(
        "Magasin",
        back_populates="offres"
    )


# =====================================================
# 🧠 PANIER OPTIMISÉ
# =====================================================

class PanierOptimise(Base):

    __tablename__ = "panier_optimise"

    id_panier = Column(
        Integer,
        primary_key=True,
        index=True
    )

    total_panier = Column(
        Float,
        nullable=False
    )

    economie = Column(
        Float,
        default=0
    )

    scenario = Column(
        String,
        nullable=False
    )

    date_optimisation = Column(
        DateTime,
        default=datetime.utcnow
    )

    id_liste = Column(
        Integer,
        ForeignKey("listes_courses.id_liste"),
        nullable=False
    )

    # Relations
    liste = relationship(
        "ListeCourses",
        back_populates="paniers_optimises"
    )

    items = relationship(
        "PanierOptimiseItem",
        back_populates="panier",
        cascade="all, delete-orphan"
    )


# =====================================================
# 🧾 ITEMS PANIER OPTIMISÉ
# =====================================================

class PanierOptimiseItem(Base):

    __tablename__ = "panier_optimise_items"

    id_item = Column(
        Integer,
        primary_key=True,
        index=True
    )

    id_panier = Column(
        Integer,
        ForeignKey("panier_optimise.id_panier"),
        nullable=False
    )

    id_produit = Column(
        Integer,
        ForeignKey("produits.id_produit"),
        nullable=False
    )

    id_magasin = Column(
        Integer,
        ForeignKey("magasins.id_magasin"),
        nullable=False
    )

    prix_choisi = Column(
        Float,
        nullable=False
    )

    quantite = Column(
        Integer,
        nullable=False
    )

    sous_total = Column(
        Float,
        nullable=False
    )

    # Relations
    panier = relationship(
        "PanierOptimise",
        back_populates="items"
    )

    produit = relationship(
        "Produit",
        back_populates="panier_items"
    )

    magasin = relationship(
        "Magasin",
        back_populates="panier_items"
    )