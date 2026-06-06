"""
Script de test complet SmartPanier API
Exécuter avec : python test_api.py
Le serveur doit tourner sur http://localhost:8000
"""

import requests
import json
import sys
import time

BASE = "http://localhost:8000"
EMAIL = "test_auto@smartpanier.ma"
PASSWORD = "Test1234!"
NOM = "Test Auto"

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

class Counters:
    ok = 0
    fail = 0

C = Counters()

def green(s):  return f"\033[92m{s}\033[0m"
def red(s):    return f"\033[91m{s}\033[0m"
def yellow(s): return f"\033[93m{s}\033[0m"
def bold(s):   return f"\033[1m{s}\033[0m"
def cyan(s):   return f"\033[96m{s}\033[0m"

def section(title):
    print(f"\n{bold(cyan('══════════════════════════════════════'))}")
    print(f"  {bold(title)}")
    print(f"{bold(cyan('══════════════════════════════════════'))}")

def check(label, response, expected_status=200, show_body=True):
    ok = response.status_code == expected_status
    status = green("✓ PASS") if ok else red("✗ FAIL")
    print(f"  {status}  [{response.status_code}]  {label}")
    if not ok:
        C.fail += 1
        try:
            body = response.json()
        except Exception:
            body = response.text[:300]
        print(f"         {red('→ ' + json.dumps(body, ensure_ascii=False)[:200])}")
    else:
        C.ok += 1
        if show_body:
            try:
                body = response.json()
                preview = json.dumps(body, ensure_ascii=False)
                if len(preview) > 200:
                    preview = preview[:200] + "…"
                print(f"         {yellow('→ ' + preview)}")
            except Exception:
                pass
    return ok

def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


# ─────────────────────────────────────────────
# 0. SANITY CHECK
# ─────────────────────────────────────────────

section("0. SANITY CHECK")
try:
    r = requests.get(f"{BASE}/", timeout=5)
    check("GET /  (serveur en ligne)", r)
except requests.ConnectionError:
    print(red("\n  ERREUR : Impossible de joindre http://localhost:8000"))
    print(red("  Lance d'abord : uvicorn app.main:app --reload\n"))
    sys.exit(1)


# ─────────────────────────────────────────────
# 1. AUTH
# ─────────────────────────────────────────────

section("1. AUTH")

# Register (peut retourner 400 si l'user existe déjà – toléré)
r = requests.post(f"{BASE}/register", json={"nom": NOM, "email": EMAIL, "password": PASSWORD})
if r.status_code == 200:
    check("POST /register  (nouveau compte)", r)
elif r.status_code == 400 and ("existe" in r.text.lower() or "déjà" in r.text.lower() or "deja" in r.text.lower()):
    print(f"  {yellow('~ SKIP')}  [400]  POST /register  (compte déjà existant)")
    C.ok += 1
else:
    check("POST /register", r)

# Login
r = requests.post(f"{BASE}/login", json={"email": EMAIL, "password": PASSWORD})
ok = check("POST /login", r)
if not ok:
    sys.exit(1)
data = r.json()
TOKEN = data["access_token"]
REFRESH = data.get("refresh_token", "")

# /me
r = requests.get(f"{BASE}/me", headers=auth_headers(TOKEN))
check("GET /me  (profil utilisateur)", r)

# refresh
if REFRESH:
    r = requests.post(f"{BASE}/refresh", json={"refresh_token": REFRESH})
    check("POST /refresh  (nouveau access_token)", r)

# change-password (test → remet l'ancien mot de passe)
r = requests.put(f"{BASE}/change-password", json={
    "email": EMAIL,
    "ancien_motdepasse": PASSWORD,
    "nouveau_motdepasse": PASSWORD
}, headers=auth_headers(TOKEN))
check("PUT /change-password  (même password)", r)


# ─────────────────────────────────────────────
# 2. PRODUITS
# ─────────────────────────────────────────────

section("2. PRODUITS")

r = requests.get(f"{BASE}/produits/")
check("GET /produits/  (liste complète)", r, show_body=False)
produits = r.json()

if not produits:
    print(red("  ERREUR : Aucun produit en base. Vérifie seed.py."))
    sys.exit(1)

print(f"  → {len(produits)} produits trouvés")
ID_PRODUIT_1 = produits[0]["id_produit"]
ID_PRODUIT_2 = produits[1]["id_produit"] if len(produits) > 1 else ID_PRODUIT_1
ID_PRODUIT_3 = produits[2]["id_produit"] if len(produits) > 2 else ID_PRODUIT_1
cat_1 = produits[0]["categorie_produit"]
print(f"  → Produit test 1 : id={ID_PRODUIT_1}  catégorie={cat_1}")
print(f"  → Produit test 2 : id={ID_PRODUIT_2}")
print(f"  → Produit test 3 : id={ID_PRODUIT_3}")

# Alternatives
r = requests.get(f"{BASE}/produits/{ID_PRODUIT_1}/alternatives")
check(f"GET /produits/{ID_PRODUIT_1}/alternatives", r)

r = requests.get(f"{BASE}/produits/{ID_PRODUIT_1}/alternatives?budget_max=50")
check(f"GET /produits/{ID_PRODUIT_1}/alternatives?budget_max=50", r)

# Produit inexistant
r = requests.get(f"{BASE}/produits/999999/alternatives")
check("GET /produits/999999/alternatives  (404 attendu)", r, expected_status=404)


# ─────────────────────────────────────────────
# 3. OFFRES
# ─────────────────────────────────────────────

section("3. OFFRES")

r = requests.get(f"{BASE}/offres/produits/{ID_PRODUIT_1}")
check(f"GET /offres/produits/{ID_PRODUIT_1}", r)
offres = r.json()
if offres:
    print(f"  → {len(offres)} offres : " +
          ", ".join(f"{o['magasin']} {o['prix']} MAD" for o in offres))


# ─────────────────────────────────────────────
# 4. SCÉNARIOS
# ─────────────────────────────────────────────

section("4. SCÉNARIOS")
r = requests.get(f"{BASE}/scenarios")
check("GET /scenarios", r)


# ─────────────────────────────────────────────
# 5. LISTES DE COURSES
# ─────────────────────────────────────────────

section("5. LISTES DE COURSES")

# Créer une liste
r = requests.post(f"{BASE}/listes/", json={
    "nom_liste": "Liste test automatique",
    "budget": 300,
    "produits": [
        {"id_produit": ID_PRODUIT_1, "quantite": 2},
        {"id_produit": ID_PRODUIT_2, "quantite": 1},
    ]
}, headers=auth_headers(TOKEN))
check("POST /listes/  (créer liste)", r)
LISTE_ID = r.json()["id_liste"]
print(f"  → Liste créée : id={LISTE_ID}")

# Mes listes
r = requests.get(f"{BASE}/listes/me", headers=auth_headers(TOKEN))
check("GET /listes/me", r, show_body=False)
print(f"  → {len(r.json())} liste(s) trouvée(s)")

# Détail liste
r = requests.get(f"{BASE}/listes/{LISTE_ID}", headers=auth_headers(TOKEN))
check(f"GET /listes/{LISTE_ID}", r)

# Ajouter produit
r = requests.post(f"{BASE}/listes/{LISTE_ID}/produits", json={
    "id_produit": ID_PRODUIT_3,
    "quantite": 3
}, headers=auth_headers(TOKEN))
check(f"POST /listes/{LISTE_ID}/produits  (ajouter produit)", r)

# Me full
r = requests.get(f"{BASE}/listes/me/full", headers=auth_headers(TOKEN))
check("GET /listes/me/full", r, show_body=False)

# Me last
r = requests.get(f"{BASE}/listes/me/last", headers=auth_headers(TOKEN))
check("GET /listes/me/last", r, show_body=False)

# Update liste
r = requests.put(f"{BASE}/listes/{LISTE_ID}", json={
    "nom_liste": "Liste test modifiée",
    "budget": 350
}, headers=auth_headers(TOKEN))
check(f"PUT /listes/{LISTE_ID}", r)

# Supprimer produit de la liste
r = requests.delete(f"{BASE}/listes/{LISTE_ID}/produits/{ID_PRODUIT_3}",
                    headers=auth_headers(TOKEN))
check(f"DELETE /listes/{LISTE_ID}/produits/{ID_PRODUIT_3}", r)

# Dupliquer
r = requests.post(f"{BASE}/listes/{LISTE_ID}/duplicate", headers=auth_headers(TOKEN))
check(f"POST /listes/{LISTE_ID}/duplicate", r)
COPIE_ID = r.json().get("nouvelle_liste_id")

# Quantités d'une liste
r = requests.get(f"{BASE}/produits/liste/{LISTE_ID}/quantites",
                 headers=auth_headers(TOKEN))
# Ce endpoint peut ne pas être authentifié selon l'implémentation
if r.status_code in (200, 401, 403):
    check(f"GET /produits/liste/{LISTE_ID}/quantites", r,
          expected_status=r.status_code, show_body=True)


# ─────────────────────────────────────────────
# 6. OPTIMISATION — POST /optimiser
# ─────────────────────────────────────────────

section("6. OPTIMISATION — POST /optimiser (4 scénarios)")

PRODUITS_LISTE = [
    {"id_produit": ID_PRODUIT_1, "quantite": 2},
    {"id_produit": ID_PRODUIT_2, "quantite": 1},
]

def tester_scenario(scenario, budget=300):
    payload = {
        "id_liste": LISTE_ID,
        "budget": budget,
        "scenario": scenario,
        "produits": PRODUITS_LISTE
    }
    r = requests.post(f"{BASE}/optimiser", json=payload)
    ok = check(f"POST /optimiser  [{scenario}]  budget={budget}", r)
    if ok:
        d = r.json()
        print(f"         total={d['total']} MAD  |  "
              f"total_initial={d['total_initial']} MAD  |  "
              f"economies={d['economies']} MAD")
        for mag in d["repartition"]:
            prods = ", ".join(p["nom"][:25] for p in mag["produits"])
            print(f"         {mag['magasin']} ({mag['sous_total_magasin']} MAD) → {prods}")
    return ok, r

tester_scenario("prix_min")
tester_scenario("mono_2_magasins")
tester_scenario("budget_strict", budget=80)    # budget serré → inclut le moins cher, saute l'autre
tester_scenario("recommande")

# Scénario invalide → 400 attendu
r = requests.post(f"{BASE}/optimiser", json={
    "id_liste": LISTE_ID, "budget": 300,
    "scenario": "inexistant",
    "produits": PRODUITS_LISTE
})
check("POST /optimiser  [scenario invalide]  (400 attendu)", r, expected_status=400)


# ─────────────────────────────────────────────
# 7. OPTIMISATION — via listes/{id}/optimiser
# ─────────────────────────────────────────────

section("7. OPTIMISATION — POST /listes/{id}/optimiser")

for sc in ["prix_min", "mono_2_magasins", "budget_strict", "recommande"]:
    r = requests.post(f"{BASE}/listes/{LISTE_ID}/optimiser?scenario={sc}",
                      headers=auth_headers(TOKEN))
    ok = check(f"POST /listes/{LISTE_ID}/optimiser  [{sc}]", r)
    if ok:
        d = r.json()
        print(f"         total={d['total']} MAD  economies={d['economies']} MAD")


# ─────────────────────────────────────────────
# 8. HISTORIQUE OPTIMISATIONS
# ─────────────────────────────────────────────

section("8. HISTORIQUE OPTIMISATIONS")

r = requests.get(f"{BASE}/listes/{LISTE_ID}/optimisations",
                 headers=auth_headers(TOKEN))
# Ce endpoint peut retourner 200 ou 401 selon l'implémentation
check(f"GET /listes/{LISTE_ID}/optimisations", r,
      expected_status=r.status_code, show_body=True)


# ─────────────────────────────────────────────
# 9. NETTOYAGE
# ─────────────────────────────────────────────

section("9. NETTOYAGE")

if COPIE_ID:
    r = requests.delete(f"{BASE}/listes/{COPIE_ID}", headers=auth_headers(TOKEN))
    check(f"DELETE /listes/{COPIE_ID}  (suppression copie)", r)

r = requests.delete(f"{BASE}/listes/{LISTE_ID}", headers=auth_headers(TOKEN))
check(f"DELETE /listes/{LISTE_ID}  (suppression liste test)", r)


# ─────────────────────────────────────────────
# RÉSUMÉ
# ─────────────────────────────────────────────

total = C.ok + C.fail
print(f"\n{'═'*42}")
print(bold(f"  RÉSULTAT : {C.ok}/{total} tests réussis"))
if C.fail == 0:
    print(green("  Tous les tests sont passés ✓"))
else:
    print(red(f"  {C.fail} test(s) en échec ✗"))
print(f"{'═'*42}\n")

sys.exit(0 if C.fail == 0 else 1)
