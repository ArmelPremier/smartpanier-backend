import random

# =========================
# 🏪 MAGASINS
# =========================
magasins = [
    {"id": 1, "nom": "Marjane"},
    {"id": 2, "nom": "Carrefour"},
]

# =========================
# 📦 PRODUITS (SANS QUANTITÉ)
# =========================
produits = [

# 🥦 Fruits et légumes
{"nom": "Tomate ronde", "categorie": "Fruits et légumes"},
{"nom": "Pomme Golden", "categorie": "Fruits et légumes"},
{"nom": "Banane", "categorie": "Fruits et légumes"},
{"nom": "Carotte", "categorie": "Fruits et légumes"},
{"nom": "Oignon rouge", "categorie": "Fruits et légumes"},
{"nom": "Courgette", "categorie": "Fruits et légumes"},
{"nom": "Poivron rouge", "categorie": "Fruits et légumes"},
{"nom": "Orange à jus", "categorie": "Fruits et légumes"},
{"nom": "Pomme de terre", "categorie": "Fruits et légumes"},
{"nom": "Fraise", "categorie": "Fruits et légumes"},

# 🍗 Boucheries
{"nom": "Poulet entier", "categorie": "Boucheries et volailles"},
{"nom": "Escalope de poulet", "categorie": "Boucheries et volailles"},
{"nom": "Steak haché", "categorie": "Boucheries et volailles"},
{"nom": "Côtelettes d’agneau", "categorie": "Boucheries et volailles"},
{"nom": "Merguez", "categorie": "Boucheries et volailles"},
{"nom": "Dinde escalope", "categorie": "Boucheries et volailles"},
{"nom": "Viande hachée", "categorie": "Boucheries et volailles"},
{"nom": "Poulet cuisse", "categorie": "Boucheries et volailles"},
{"nom": "Foie de poulet", "categorie": "Boucheries et volailles"},
{"nom": "Saucisse de bœuf", "categorie": "Boucheries et volailles"},

# 🧀 Fromage
{"nom": "Fromage Edam", "categorie": "Fromage et charcuterie"},
{"nom": "Fromage Gouda", "categorie": "Fromage et charcuterie"},
{"nom": "Fromage fondu", "categorie": "Fromage et charcuterie"},
{"nom": "Jambon de dinde", "categorie": "Fromage et charcuterie"},
{"nom": "Jambon fumé", "categorie": "Fromage et charcuterie"},
{"nom": "Saucisson sec", "categorie": "Fromage et charcuterie"},
{"nom": "Fromage râpé", "categorie": "Fromage et charcuterie"},
{"nom": "Fromage mozzarella", "categorie": "Fromage et charcuterie"},
{"nom": "Fromage camembert", "categorie": "Fromage et charcuterie"},
{"nom": "Fromage kiri", "categorie": "Fromage et charcuterie"},

# 💊 Parapharmacie
{"nom": "Gel douche", "categorie": "Parapharmacie"},
{"nom": "Shampoing", "categorie": "Parapharmacie"},
{"nom": "Savon solide", "categorie": "Parapharmacie"},
{"nom": "Dentifrice", "categorie": "Parapharmacie"},
{"nom": "Crème hydratante", "categorie": "Parapharmacie"},
{"nom": "Déodorant spray", "categorie": "Parapharmacie"},
{"nom": "Lingettes bébé", "categorie": "Parapharmacie"},
{"nom": "Gel antibactérien", "categorie": "Parapharmacie"},
{"nom": "Crème solaire SPF50", "categorie": "Parapharmacie"},
{"nom": "Coton hydrophile", "categorie": "Parapharmacie"},

# 🥛 Laitiers
{"nom": "Lait demi-écrémé", "categorie": "Produits laitiers et œufs"},
{"nom": "Yaourt nature", "categorie": "Produits laitiers et œufs"},
{"nom": "Beurre", "categorie": "Produits laitiers et œufs"},
{"nom": "Fromage blanc", "categorie": "Produits laitiers et œufs"},
{"nom": "Crème fraîche", "categorie": "Produits laitiers et œufs"},
{"nom": "Lait entier", "categorie": "Produits laitiers et œufs"},
{"nom": "Yaourt aux fruits", "categorie": "Produits laitiers et œufs"},
{"nom": "Œufs", "categorie": "Produits laitiers et œufs"},
{"nom": "Lait chocolaté", "categorie": "Produits laitiers et œufs"},
{"nom": "Dessert flan", "categorie": "Produits laitiers et œufs"},

# 💧 Eaux
{"nom": "Eau minérale", "categorie": "Eaux"},
{"nom": "Eau gazeuse", "categorie": "Eaux"},
{"nom": "Pack eau", "categorie": "Eaux"},
{"nom": "Eau aromatisée", "categorie": "Eaux"},
{"nom": "Eau de source", "categorie": "Eaux"},
{"nom": "Eau citron", "categorie": "Eaux"},
{"nom": "Eau premium", "categorie": "Eaux"},
{"nom": "Eau sport", "categorie": "Eaux"},
{"nom": "Eau familiale", "categorie": "Eaux"},
{"nom": "Eau naturelle", "categorie": "Eaux"},

# 🥤 Boissons
{"nom": "Coca-Cola", "categorie": "Boissons"},
{"nom": "Jus d’orange", "categorie": "Boissons"},
{"nom": "Thé glacé", "categorie": "Boissons"},
{"nom": "Boisson énergétique", "categorie": "Boissons"},
{"nom": "Jus multifruit", "categorie": "Boissons"},
{"nom": "Soda citron", "categorie": "Boissons"},
{"nom": "Jus pomme", "categorie": "Boissons"},
{"nom": "Boisson orange", "categorie": "Boissons"},
{"nom": "Limonade", "categorie": "Boissons"},
{"nom": "Jus mangue", "categorie": "Boissons"},
]

# =========================
# 📏 QUANTITÉS PAR CATÉGORIE
# =========================
def get_quantite(categorie):
    if "Fruits" in categorie:
        return "1kg"
    if "Boucheries" in categorie:
        return "500g"
    if "Fromage" in categorie:
        return "200g"
    if "Parapharmacie" in categorie:
        return "1 unité"
    if "laitiers" in categorie.lower():
        return "1L"
    if "Eaux" in categorie:
        return "1.5L"
    if "Boissons" in categorie:
        return "1L"
    return "1 unité"

# =========================
# 💰 PRIX RÉALISTES
# =========================
def generate_price(categorie):
    if "Fruits" in categorie:
        return random.uniform(2, 10)
    if "Boucheries" in categorie:
        return random.uniform(40, 90)
    if "Fromage" in categorie:
        return random.uniform(10, 30)
    if "Parapharmacie" in categorie:
        return random.uniform(15, 60)
    if "laitiers" in categorie.lower():
        return random.uniform(3, 12)
    if "Eaux" in categorie:
        return random.uniform(1.5, 6)
    if "Boissons" in categorie:
        return random.uniform(3, 12)
    return random.uniform(5, 20)

# =========================
# 🏷️ OFFRES
# =========================
offres = []

for i, produit in enumerate(produits, start=1):
    base_price = generate_price(produit["categorie"])

    for magasin in magasins:
        variation = random.uniform(-1, 1)
        prix = round(base_price + variation, 2)

        offres.append({
            "id_produit": i,
            "id_magasin": magasin["id"],
            "prix_offre": prix,
            "promotion": magasin["nom"] == "Marjane",
            "stock": random.randint(50, 150),
            "quantite": get_quantite(produit["categorie"])
        })