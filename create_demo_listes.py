"""
Crée 10 listes de démonstration pour la soutenance SmartPanier.

Chaque liste est conçue pour mettre en valeur un scénario précis.
Les listes déjà existantes pour cet utilisateur sont supprimées en début de script.

Usage:
    uvicorn app.main:app --reload   # dans un autre terminal
    python create_demo_listes.py
"""
import requests
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE = "http://localhost:8000"
EMAIL = "test_auto@smartpanier.ma"
PASSWORD = "Test1234!"

# ─── Authentification ────────────────────────────────────────────────────────

r = requests.post(f"{BASE}/login", json={"email": EMAIL, "password": PASSWORD})
if r.status_code != 200:
    print(f"[ERREUR] Login echoue : {r.text[:200]}")
    sys.exit(1)

TOKEN = r.json()["access_token"]
H = {"Authorization": f"Bearer {TOKEN}"}

# ─── Nettoyage des listes existantes ─────────────────────────────────────────

existing = requests.get(f"{BASE}/listes/me", headers=H)
if existing.status_code == 200:
    listes_actuelles = existing.json()
    if listes_actuelles:
        print(f"Suppression de {len(listes_actuelles)} liste(s) existante(s)...")
        for l in listes_actuelles:
            requests.delete(f"{BASE}/listes/{l['id_liste']}", headers=H)

# ─── Définition des 10 listes ────────────────────────────────────────────────
#
# Produits cross-store disponibles (IDs après seed.py) :
#
#  ID=291 Pistaches Fancy 125g         MY=55.15  | MP=144.0   → MY gagne
#  ID=299 Amandes Fancy 120g           MY=51.41  | MP=90.0    → MY gagne
#  ID=302 Figues sechees 1Kg           MY=135.0  | MP=94.0    → MP gagne
#  ID=307 Bai De Goji                  MY=29 seulement
#  ID=314 Piment Doux 250G             MY=11.84  | MP=55.0    → MY gagne
#  ID=315 Piment Fort 250G             MY=13.18  | MP=38.0    → MY gagne
#  ID=316 Curcuma 250G                 MY=11.28  | MP=40.0    → MY gagne
#  ID=317 Poivre Noir 250G             MY=26.26  | MP=100.0   → MY gagne
#  ID=318 Gingembre 250G               MY=19.40  | MP=82.0    → MY gagne
#  ID=319 Cumin 250G                   MY=16.50  | MP=69.0    → MY gagne
#  ID=330 Huile olive 1/2L             MY=27.95  | MP=75.0    → MY gagne
#  ID=337 Huile de table 10L           MY=8.90   | MP=85.0    → MY gagne
#  ID=342 Spaghetti 500g               MY=25.29  | MP=15.0    → MP gagne
#  ID=344 Penne 500g                   MY=28.70  | MP=15.0    → MP gagne
#  ID=351 Tagliatelle 500g             MY=36.91  | MP=23.0    → MP gagne
#  ID=353 Riz 1kg                      MY=39.58  | MP=21.0    → MP gagne
#  ID=362 Thon naturel 85g             MY=11.95  | MP=115.0   → MY gagne
#  ID=363 Mais                         MY=7.2  seulement
#  ID=366 Thon a l'huile 85g           MY=12.0   | MP=7.0     → MP gagne
#  ID=367 Sardines                     MY=12 seulement
#  ID=372 Champignons 355g             MY=16.49  | MP=16.0    → MP gagne
#  ID=387 Raisins secs                 MP=41 seulement
#  ID=423 Tomate concentree            MP=32 seulement

LISTES = [
    # ── 1. Prix minimum — split épices MY / pâtes MP ──────────────────────
    {
        "nom": "1. Pates a la sauce tomate",
        "budget": 250,
        "note": "prix_min : épices MY (11-27 MAD) vs pates MP (15 MAD) → split parfait",
        "highlight": ["prix_min", "mono_2_magasins"],
        "produits": [
            {"id_produit": 342, "quantite": 3},   # Spaghetti   MY 25.29 | MP 15  → MP
            {"id_produit": 315, "quantite": 1},   # Piment Fort MY 13.18 | MP 38  → MY
            {"id_produit": 330, "quantite": 1},   # Huile olive MY 27.95 | MP 75  → MY
            {"id_produit": 319, "quantite": 1},   # Cumin       MY 16.50 | MP 69  → MY
            {"id_produit": 423, "quantite": 1},   # Tomate cone MP 32 seulement
        ],
        # Min total: 45+13.18+27.95+16.50+32 = 134.63 MAD < 250 → tous scénarios OK
    },
    # ── 2. Prix minimum — riz + légumes, cross-store évident ──────────────
    {
        "nom": "2. Riz aux legumes du marche",
        "budget": 200,
        "note": "riz+champignons a MP (21+16 MAD), épices a MY (11-19 MAD)",
        "highlight": ["prix_min", "mono_2_magasins"],
        "produits": [
            {"id_produit": 353, "quantite": 2},   # Riz         MY 39.58 | MP 21  → MP
            {"id_produit": 316, "quantite": 1},   # Curcuma     MY 11.28 | MP 40  → MY
            {"id_produit": 318, "quantite": 1},   # Gingembre   MY 19.40 | MP 82  → MY
            {"id_produit": 314, "quantite": 1},   # Piment Doux MY 11.84 | MP 55  → MY
            {"id_produit": 372, "quantite": 2},   # Champignons MY 16.49 | MP 16  → MP
        ],
        # Min total: 42+11.28+19.40+11.84+32 = 116.52 MAD < 200 → tous scénarios OK
    },
    # ── 3. Recommandé — épices 4-6x moins chères à MY ─────────────────────
    {
        "nom": "3. Tajine de boeuf marocain",
        "budget": 200,
        "note": "economies massives : épices 4-7x moins chères a MY (cumin 16 MY vs 69 MP)",
        "highlight": ["recommande", "prix_min"],
        "produits": [
            {"id_produit": 316, "quantite": 2},   # Curcuma     MY 11.28 | MP 40  → MY
            {"id_produit": 318, "quantite": 1},   # Gingembre   MY 19.40 | MP 82  → MY
            {"id_produit": 319, "quantite": 2},   # Cumin       MY 16.50 | MP 69  → MY
            {"id_produit": 315, "quantite": 1},   # Piment Fort MY 13.18 | MP 38  → MY
            {"id_produit": 314, "quantite": 1},   # Piment Doux MY 11.84 | MP 55  → MY
            {"id_produit": 353, "quantite": 1},   # Riz         MY 39.58 | MP 21  → MP
        ],
        # Min total: 22.56+19.40+33+13.18+11.84+21 = 120.98 MAD < 200 → tous OK
    },
    # ── 4. Budget strict — coupe intelligente quand total > budget ─────────
    {
        "nom": "4. Budget etudiant strict 70 MAD",
        "budget": 70,
        "note": "budget_strict : 5 produits->81.7 MAD min, coupe intelligente sous 70 MAD",
        "highlight": ["budget_strict"],
        "produits": [
            {"id_produit": 342, "quantite": 2},   # Spaghetti   MP 15    → 30 MAD
            {"id_produit": 372, "quantite": 1},   # Champignons MP 16    → 16 MAD
            {"id_produit": 319, "quantite": 1},   # Cumin       MY 16.50 → 16.5 MAD
            {"id_produit": 367, "quantite": 1},   # Sardines    MY 12    → 12 MAD (sera coupé)
            {"id_produit": 363, "quantite": 1},   # Mais        MY 7.2   → 7.2 MAD
        ],
        # Min total: 30+16+16.5+12+7.2 = 81.7 > 70
        # → budget_strict coupe; mono_2_magasins retourne [SKIP] (attendu)
    },
    # ── 5. Prix minimum — fruits secs, split MY / MP très visible ─────────
    {
        "nom": "5. Aperitif fruits secs",
        "budget": 400,
        "note": "pistaches+amandes 2-3x moins chères a MY; figues+raisins moins chers a MP",
        "highlight": ["prix_min", "mono_2_magasins"],
        "produits": [
            {"id_produit": 291, "quantite": 2},   # Pistaches   MY 55.15 | MP 144 → MY
            {"id_produit": 299, "quantite": 1},   # Amandes     MY 51.41 | MP 90  → MY
            {"id_produit": 302, "quantite": 1},   # Figues      MY 135   | MP 94  → MP
            {"id_produit": 387, "quantite": 1},   # Raisins sec MP 41 seulement
            {"id_produit": 307, "quantite": 1},   # Bai De Goji MY 29 seulement
        ],
        # Min total: 110.30+51.41+94+41+29 = 325.71 MAD < 400 → tous OK
    },
    # ── 6. Recommandé — 7 produits cross-store, qualité/prix optimal ───────
    {
        "nom": "6. Semaine equilibree complete",
        "budget": 300,
        "note": "7 produits cross-store : recommandé arbitre qualité/prix sur chaque rayon",
        "highlight": ["recommande", "mono_2_magasins"],
        "produits": [
            {"id_produit": 342, "quantite": 2},   # Spaghetti   MY 25.29 | MP 15  → MP
            {"id_produit": 351, "quantite": 1},   # Tagliatelle MY 36.91 | MP 23  → MP
            {"id_produit": 314, "quantite": 1},   # Piment Doux MY 11.84 | MP 55  → MY
            {"id_produit": 319, "quantite": 1},   # Cumin       MY 16.50 | MP 69  → MY
            {"id_produit": 330, "quantite": 1},   # Huile olive MY 27.95 | MP 75  → MY
            {"id_produit": 353, "quantite": 1},   # Riz         MY 39.58 | MP 21  → MP
            {"id_produit": 372, "quantite": 1},   # Champignons MY 16.49 | MP 16  → MP
        ],
        # Min total: 30+23+11.84+16.50+27.95+21+16 = 146.29 MAD < 300 → tous OK
    },
    # ── 7. Mono 2 magasins — cuisineitalienne, toutes pâtes à MP ──────────
    {
        "nom": "7. Cuisine italienne complete",
        "budget": 180,
        "note": "mono_2_magasins : toutes pates a MP (15-23 MAD), huile+épice a MY",
        "highlight": ["mono_2_magasins", "prix_min"],
        "produits": [
            {"id_produit": 351, "quantite": 2},   # Tagliatelle MY 36.91 | MP 23  → MP
            {"id_produit": 342, "quantite": 2},   # Spaghetti   MY 25.29 | MP 15  → MP
            {"id_produit": 344, "quantite": 2},   # Penne       MY 28.70 | MP 15  → MP
            {"id_produit": 330, "quantite": 1},   # Huile olive MY 27.95 | MP 75  → MY
            {"id_produit": 315, "quantite": 1},   # Piment Fort MY 13.18 | MP 38  → MY
        ],
        # Min total: 46+30+30+27.95+13.18 = 147.13 MAD < 180 → tous OK
    },
    # ── 8. Budget strict — conserves, coupe la sardine ────────────────────
    {
        "nom": "8. Conserves urgence budget 60 MAD",
        "budget": 60,
        "note": "budget_strict 60 MAD : total min=66.3 MAD, coupe sardines pour tenir budget",
        "highlight": ["budget_strict"],
        "produits": [
            {"id_produit": 362, "quantite": 2},   # Thon naturel MY 11.95 | MP 115 → MY
            {"id_produit": 372, "quantite": 1},   # Champignons  MY 16.49 | MP 16  → MP
            {"id_produit": 363, "quantite": 2},   # Mais         MY 7.2 seulement
            {"id_produit": 367, "quantite": 1},   # Sardines     MY 12 seulement (sera coupé)
        ],
        # Min total: 23.9+16+14.4+12 = 66.3 > 60
        # → budget_strict coupe sardines → 54.3 MAD; mono echoue (attendu)
    },
    # ── 9. Toutes catégories — economies cumulées sur grande liste ─────────
    {
        "nom": "9. Garde-manger mensuel complet",
        "budget": 600,
        "note": "grande liste 3 catégories : economies cumulées sur tout le mois",
        "highlight": ["prix_min", "mono_2_magasins"],
        "produits": [
            {"id_produit": 342, "quantite": 5},   # Spaghetti x5  MP 15    → 75 MAD
            {"id_produit": 353, "quantite": 3},   # Riz x3        MP 21    → 63 MAD
            {"id_produit": 330, "quantite": 2},   # Huile olive x2 MY 27.95 → 55.90 MAD
            {"id_produit": 314, "quantite": 2},   # Piment Doux x2 MY 11.84 → 23.68 MAD
            {"id_produit": 316, "quantite": 2},   # Curcuma x2    MY 11.28 → 22.56 MAD
            {"id_produit": 319, "quantite": 2},   # Cumin x2      MY 16.50 → 33 MAD
            {"id_produit": 302, "quantite": 1},   # Figues        MP 94    → 94 MAD
            {"id_produit": 372, "quantite": 3},   # Champignons x3 MP 16   → 48 MAD
        ],
        # Min total: 75+63+55.90+23.68+22.56+33+94+48 = 415.14 MAD < 600 → tous OK
    },
    # ── 10. Mono 2 magasins — démonstration chiffrée split vs 1 magasin ───
    {
        "nom": "10. Demo mono magasin vs split",
        "budget": 400,
        "note": "mono_2_magasins : MY seul=326 MAD | MP seul=438 MAD | split=237 MAD",
        "highlight": ["mono_2_magasins"],
        "produits": [
            {"id_produit": 291, "quantite": 1},   # Pistaches   MY 55.15 | MP 144 → MY
            {"id_produit": 351, "quantite": 2},   # Tagliatelle MY 36.91 | MP 23  → MP
            {"id_produit": 314, "quantite": 1},   # Piment Doux MY 11.84 | MP 55  → MY
            {"id_produit": 342, "quantite": 2},   # Spaghetti   MY 25.29 | MP 15  → MP
            {"id_produit": 302, "quantite": 1},   # Figues      MY 135   | MP 94  → MP
        ],
        # Min total: 55.15+46+11.84+30+94 = 236.99 MAD < 400 → tous OK
        # MY seul: 55.15+73.82+11.84+50.58+135 = 326.39 MAD
        # MP seul: 144+46+55+30+94 = 369 MAD (MP n'a pas Pistaches MY-only)
    },
]


# ─── Fonction d'appel d'un scénario ──────────────────────────────────────────

def run_scenario(liste_id, produits, scenario, budget):
    """Lance un scénario, retourne un résumé ou [SKIP] si 400."""
    r = requests.post(
        f"{BASE}/optimiser",
        json={
            "id_liste": liste_id,
            "budget": budget,
            "scenario": scenario,
            "produits": produits,
        },
    )
    if r.status_code == 400:
        detail = r.json().get("detail", r.text[:80])
        return f"    [SKIP] {detail}"
    if r.status_code != 200:
        return f"    [ERREUR {r.status_code}] {r.text[:100]}"

    d = r.json()
    lines = [
        f"    total={d['total']:.2f} MAD  economies={d['economies']:.2f} MAD"
        f"  (initial={d['total_initial']:.2f} MAD)"
    ]
    for mag in d["repartition"]:
        prods = ", ".join(
            f"{p['nom'][:22]}x{p['quantite']}" for p in mag["produits"]
        )
        lines.append(
            f"    {mag['magasin']:12} ({mag['sous_total_magasin']:.2f} MAD) → {prods}"
        )
    return "\n".join(lines)


# ─── Création et test de chaque liste ────────────────────────────────────────

print("=" * 65)
print("  CREATION ET TEST DES 10 LISTES DE DEMO SOUTENANCE")
print("=" * 65)

ids_crees = []

for i, L in enumerate(LISTES, 1):
    r = requests.post(
        f"{BASE}/listes/",
        json={"nom_liste": L["nom"], "budget": L["budget"], "produits": L["produits"]},
        headers=H,
    )
    if r.status_code != 200:
        print(f"\n[ERREUR] Impossible de creer la liste {i} : {r.text[:150]}")
        continue

    lid = r.json()["id_liste"]
    ids_crees.append(lid)

    print(f"\n{'─'*65}")
    print(f"  Liste {lid} : {L['nom']}")
    print(f"  Budget : {L['budget']} MAD  |  Focus : {', '.join(L['highlight'])}")
    print(f"  {L['note']}")
    print()

    for scenario in ["prix_min", "mono_2_magasins", "budget_strict", "recommande"]:
        star = " *" if scenario in L["highlight"] else ""
        print(f"  [{scenario}]{star}")
        print(run_scenario(lid, L["produits"], scenario, L["budget"]))

print(f"\n{'='*65}")
print(f"  {len(ids_crees)}/10 listes creees avec succes")
if ids_crees:
    print(f"  IDs en base : {ids_crees}")
print("=" * 65)
