-- =============================================================
-- SmartPanier — Schéma PostgreSQL final
-- Base : Supabase (PostgreSQL 15)
-- Auteur : Armel Houénou — Projet PI HICA 2025-2026
-- =============================================================
--
-- Tables (8) — ordre de création respectant les FK :
--   1. utilisateurs
--   2. magasins
--   3. produits
--   4. offres
--   5. listes_courses
--   6. ligne_liste_courses
--   7. panier_optimise
--   8. panier_optimise_items
-- =============================================================


-- -------------------------------------------------------------
-- 1. UTILISATEURS
--    Comptes utilisateurs de l'application.
-- -------------------------------------------------------------
CREATE TABLE utilisateurs (
    id_utilisateur        SERIAL       PRIMARY KEY,
    nom_utilisateur       TEXT         NOT NULL,
    email_utilisateur     TEXT         NOT NULL UNIQUE,
    motdepasse_utilisateur TEXT        NOT NULL
);


-- -------------------------------------------------------------
-- 2. MAGASINS
--    Enseignes scrapées (MyMarket, MarketPro).
-- -------------------------------------------------------------
CREATE TABLE magasins (
    id_magasin  SERIAL  PRIMARY KEY,
    nom_magasin TEXT    NOT NULL
);


-- -------------------------------------------------------------
-- 3. PRODUITS
--    Catalogue normalisé — un enregistrement par produit unique
--    (même product_key partagé entre magasins pour le matching).
-- -------------------------------------------------------------
CREATE TABLE produits (
    id_produit        SERIAL   PRIMARY KEY,
    product_key       TEXT     NOT NULL UNIQUE,   -- MD5(nom_normalise + categorie)[:12]
    nom_produit       TEXT     NOT NULL,
    categorie_produit TEXT     NOT NULL,
    marque            TEXT,
    quantite          TEXT     NOT NULL,           -- ex. "500g", "1kg"
    code_normalise    TEXT,
    qualite_score     FLOAT    DEFAULT 5.0
);


-- -------------------------------------------------------------
-- 4. OFFRES
--    Prix d'un produit dans un magasin (N offres par produit
--    si plusieurs formats/tailles existent dans le même magasin).
-- -------------------------------------------------------------
CREATE TABLE offres (
    id_offre      SERIAL     PRIMARY KEY,
    prix_offre    FLOAT      NOT NULL,
    promotion     BOOLEAN    DEFAULT FALSE,
    stock         INTEGER    DEFAULT 0,
    id_produit    INTEGER    NOT NULL REFERENCES produits(id_produit)  ON DELETE CASCADE,
    id_magasin    INTEGER    NOT NULL REFERENCES magasins(id_magasin)  ON DELETE CASCADE,
    date_scraping TIMESTAMP  DEFAULT NOW()
);


-- -------------------------------------------------------------
-- 5. LISTES_COURSES
--    Listes de courses créées par les utilisateurs.
-- -------------------------------------------------------------
CREATE TABLE listes_courses (
    id_liste       SERIAL     PRIMARY KEY,
    nom_liste      TEXT       NOT NULL,
    budget         FLOAT,
    date_creation  TIMESTAMP  DEFAULT NOW(),
    id_utilisateur INTEGER    NOT NULL REFERENCES utilisateurs(id_utilisateur) ON DELETE CASCADE
);


-- -------------------------------------------------------------
-- 6. LIGNE_LISTE_COURSES
--    Produits et quantités dans une liste de courses.
-- -------------------------------------------------------------
CREATE TABLE ligne_liste_courses (
    id_ligne   SERIAL   PRIMARY KEY,
    quantite   INTEGER  NOT NULL,
    id_produit INTEGER  NOT NULL REFERENCES produits(id_produit)      ON DELETE CASCADE,
    id_liste   INTEGER  NOT NULL REFERENCES listes_courses(id_liste)  ON DELETE CASCADE
);


-- -------------------------------------------------------------
-- 7. PANIER_OPTIMISE
--    Résultat d'une optimisation (un enregistrement par appel
--    à /optimiser ou /listes/{id}/optimiser).
-- -------------------------------------------------------------
CREATE TABLE panier_optimise (
    id_panier         SERIAL     PRIMARY KEY,
    total_panier      FLOAT      NOT NULL,
    economie          FLOAT      DEFAULT 0,
    scenario          TEXT       NOT NULL,   -- prix_min | mono_2_magasins | budget_strict | recommande
    date_optimisation TIMESTAMP  DEFAULT NOW(),
    id_liste          INTEGER    NOT NULL REFERENCES listes_courses(id_liste) ON DELETE CASCADE
);


-- -------------------------------------------------------------
-- 8. PANIER_OPTIMISE_ITEMS
--    Détail produit par produit du panier optimisé.
-- -------------------------------------------------------------
CREATE TABLE panier_optimise_items (
    id_item    SERIAL   PRIMARY KEY,
    id_panier  INTEGER  NOT NULL REFERENCES panier_optimise(id_panier) ON DELETE CASCADE,
    id_produit INTEGER  NOT NULL REFERENCES produits(id_produit)       ON DELETE CASCADE,
    id_magasin INTEGER  NOT NULL REFERENCES magasins(id_magasin)       ON DELETE CASCADE,
    prix_choisi FLOAT   NOT NULL,
    quantite    INTEGER NOT NULL,
    sous_total  FLOAT   NOT NULL
);


-- =============================================================
-- INDEXES (performances)
-- =============================================================

CREATE INDEX idx_offres_produit   ON offres(id_produit);
CREATE INDEX idx_offres_magasin   ON offres(id_magasin);
CREATE INDEX idx_produits_key     ON produits(product_key);
CREATE INDEX idx_produits_cat     ON produits(categorie_produit);
CREATE INDEX idx_listes_user      ON listes_courses(id_utilisateur);
CREATE INDEX idx_lignes_liste     ON ligne_liste_courses(id_liste);
CREATE INDEX idx_panier_liste     ON panier_optimise(id_liste);
CREATE INDEX idx_items_panier     ON panier_optimise_items(id_panier);
