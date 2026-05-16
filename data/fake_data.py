import random

# =========================
# 🏪 MAGASINS
# =========================
magasins = [
    {"id": 1, "nom": "Marjane"},
    {"id": 2, "nom": "Carrefour"},
]

# =========================
# 📦 PRODUITS
# =========================
produits = [

# 🥦 Fruits et légumes
{"nom": "Tomate ronde", "categorie": "Fruits et légumes", "marque": "Les Domaines", "qualite_score": 8.2},
{"nom": "Pomme Golden", "categorie": "Fruits et légumes", "marque": "Fresh Market", "qualite_score": 8.5},
{"nom": "Banane", "categorie": "Fruits et légumes", "marque": "Dole", "qualite_score": 8.8},
{"nom": "Carotte", "categorie": "Fruits et légumes", "marque": "Green Farm", "qualite_score": 7.9},
{"nom": "Oignon rouge", "categorie": "Fruits et légumes", "marque": "Fresh Market", "qualite_score": 7.8},
{"nom": "Courgette", "categorie": "Fruits et légumes", "marque": "Les Domaines", "qualite_score": 8.1},
{"nom": "Poivron rouge", "categorie": "Fruits et légumes", "marque": "Green Farm", "qualite_score": 8.4},
{"nom": "Orange à jus", "categorie": "Fruits et légumes", "marque": "Citrus Maroc", "qualite_score": 8.7},
{"nom": "Pomme de terre", "categorie": "Fruits et légumes", "marque": "AgriPlus", "qualite_score": 7.6},
{"nom": "Fraise", "categorie": "Fruits et légumes", "marque": "BerryFresh", "qualite_score": 9.0},

# 🍗 Boucheries
{"nom": "Poulet entier", "categorie": "Boucheries et volailles", "marque": "Koutoubia", "qualite_score": 8.9},
{"nom": "Escalope de poulet", "categorie": "Boucheries et volailles", "marque": "Dawajine", "qualite_score": 8.7},
{"nom": "Steak haché", "categorie": "Boucheries et volailles", "marque": "Nabat", "qualite_score": 8.3},
{"nom": "Côtelettes d’agneau", "categorie": "Boucheries et volailles", "marque": "Beldi Meat", "qualite_score": 9.2},
{"nom": "Merguez", "categorie": "Boucheries et volailles", "marque": "Koutoubia", "qualite_score": 8.4},
{"nom": "Dinde escalope", "categorie": "Boucheries et volailles", "marque": "Dawajine", "qualite_score": 8.1},
{"nom": "Viande hachée", "categorie": "Boucheries et volailles", "marque": "Nabat", "qualite_score": 8.0},
{"nom": "Poulet cuisse", "categorie": "Boucheries et volailles", "marque": "Koutoubia", "qualite_score": 8.5},
{"nom": "Foie de poulet", "categorie": "Boucheries et volailles", "marque": "Dawajine", "qualite_score": 7.7},
{"nom": "Saucisse de bœuf", "categorie": "Boucheries et volailles", "marque": "Koutoubia", "qualite_score": 8.2},

# 🧀 Fromage
{"nom": "Fromage Edam", "categorie": "Fromage et charcuterie", "marque": "Président", "qualite_score": 8.6},
{"nom": "Fromage Gouda", "categorie": "Fromage et charcuterie", "marque": "Frico", "qualite_score": 8.7},
{"nom": "Fromage fondu", "categorie": "Fromage et charcuterie", "marque": "La Vache Qui Rit", "qualite_score": 8.9},
{"nom": "Jambon de dinde", "categorie": "Fromage et charcuterie", "marque": "Koutoubia", "qualite_score": 8.0},
{"nom": "Jambon fumé", "categorie": "Fromage et charcuterie", "marque": "Dari", "qualite_score": 8.1},
{"nom": "Saucisson sec", "categorie": "Fromage et charcuterie", "marque": "Olé", "qualite_score": 7.9},
{"nom": "Fromage râpé", "categorie": "Fromage et charcuterie", "marque": "Président", "qualite_score": 8.5},
{"nom": "Fromage mozzarella", "categorie": "Fromage et charcuterie", "marque": "Galbani", "qualite_score": 9.1},
{"nom": "Fromage camembert", "categorie": "Fromage et charcuterie", "marque": "Président", "qualite_score": 8.8},
{"nom": "Fromage kiri", "categorie": "Fromage et charcuterie", "marque": "Kiri", "qualite_score": 8.7},

# 💊 Parapharmacie
{"nom": "Gel douche", "categorie": "Parapharmacie", "marque": "Nivea", "qualite_score": 8.4},
{"nom": "Shampoing", "categorie": "Parapharmacie", "marque": "Head & Shoulders", "qualite_score": 8.8},
{"nom": "Savon solide", "categorie": "Parapharmacie", "marque": "Dove", "qualite_score": 8.1},
{"nom": "Dentifrice", "categorie": "Parapharmacie", "marque": "Colgate", "qualite_score": 8.9},
{"nom": "Crème hydratante", "categorie": "Parapharmacie", "marque": "Nivea", "qualite_score": 8.7},
{"nom": "Déodorant spray", "categorie": "Parapharmacie", "marque": "Rexona", "qualite_score": 8.2},
{"nom": "Lingettes bébé", "categorie": "Parapharmacie", "marque": "Johnson's", "qualite_score": 8.5},
{"nom": "Gel antibactérien", "categorie": "Parapharmacie", "marque": "Dettol", "qualite_score": 8.3},
{"nom": "Crème solaire SPF50", "categorie": "Parapharmacie", "marque": "La Roche-Posay", "qualite_score": 9.3},
{"nom": "Coton hydrophile", "categorie": "Parapharmacie", "marque": "Cotoneve", "qualite_score": 7.8},

# 🥛 Laitiers
{"nom": "Lait demi-écrémé", "categorie": "Produits laitiers et œufs", "marque": "Centrale Danone", "qualite_score": 8.6},
{"nom": "Yaourt nature", "categorie": "Produits laitiers et œufs", "marque": "Danone", "qualite_score": 8.5},
{"nom": "Beurre", "categorie": "Produits laitiers et œufs", "marque": "Président", "qualite_score": 9.0},
{"nom": "Fromage blanc", "categorie": "Produits laitiers et œufs", "marque": "Jibal", "qualite_score": 8.2},
{"nom": "Crème fraîche", "categorie": "Produits laitiers et œufs", "marque": "Président", "qualite_score": 8.7},
{"nom": "Lait entier", "categorie": "Produits laitiers et œufs", "marque": "Centrale Danone", "qualite_score": 8.4},
{"nom": "Yaourt aux fruits", "categorie": "Produits laitiers et œufs", "marque": "Danone", "qualite_score": 8.6},
{"nom": "Œufs", "categorie": "Produits laitiers et œufs", "marque": "Œufs Beldi", "qualite_score": 9.1},
{"nom": "Lait chocolaté", "categorie": "Produits laitiers et œufs", "marque": "Candia", "qualite_score": 8.3},
{"nom": "Dessert flan", "categorie": "Produits laitiers et œufs", "marque": "Danette", "qualite_score": 8.5},

# 💧 Eaux
{"nom": "Eau minérale", "categorie": "Eaux", "marque": "Sidi Ali", "qualite_score": 8.8},
{"nom": "Eau gazeuse", "categorie": "Eaux", "marque": "Oulmès", "qualite_score": 8.6},
{"nom": "Pack eau", "categorie": "Eaux", "marque": "Sidi Ali", "qualite_score": 8.7},
{"nom": "Eau aromatisée", "categorie": "Eaux", "marque": "Cristaline", "qualite_score": 7.9},
{"nom": "Eau de source", "categorie": "Eaux", "marque": "Aïn Saïss", "qualite_score": 8.5},
{"nom": "Eau citron", "categorie": "Eaux", "marque": "Cristaline", "qualite_score": 7.8},
{"nom": "Eau premium", "categorie": "Eaux", "marque": "Evian", "qualite_score": 9.2},
{"nom": "Eau sport", "categorie": "Eaux", "marque": "Powerade", "qualite_score": 8.0},
{"nom": "Eau familiale", "categorie": "Eaux", "marque": "Sidi Harazem", "qualite_score": 8.1},
{"nom": "Eau naturelle", "categorie": "Eaux", "marque": "Aïn Atlas", "qualite_score": 8.4},

# 🥤 Boissons
{"nom": "Coca-Cola", "categorie": "Boissons", "marque": "Coca-Cola", "qualite_score": 9.0},
{"nom": "Jus d’orange", "categorie": "Boissons", "marque": "Valencia", "qualite_score": 8.5},
{"nom": "Thé glacé", "categorie": "Boissons", "marque": "Fuze Tea", "qualite_score": 8.1},
{"nom": "Boisson énergétique", "categorie": "Boissons", "marque": "Red Bull", "qualite_score": 8.8},
{"nom": "Jus multifruit", "categorie": "Boissons", "marque": "Marrakech", "qualite_score": 8.3},
{"nom": "Soda citron", "categorie": "Boissons", "marque": "Schweppes", "qualite_score": 8.0},
{"nom": "Jus pomme", "categorie": "Boissons", "marque": "Valencia", "qualite_score": 8.2},
{"nom": "Boisson orange", "categorie": "Boissons", "marque": "Fanta", "qualite_score": 8.4},
{"nom": "Limonade", "categorie": "Boissons", "marque": "Sprite", "qualite_score": 8.1},
{"nom": "Jus mangue", "categorie": "Boissons", "marque": "Marrakech", "qualite_score": 8.6},

# 🍝 Pâtes, riz et féculents
{"nom": "Spaghetti", "categorie": "Pâtes, riz et féculents", "marque": "Panzani", "qualite_score": 8.7},
{"nom": "Macaroni", "categorie": "Pâtes, riz et féculents", "marque": "Tria", "qualite_score": 8.1},
{"nom": "Riz basmati", "categorie": "Pâtes, riz et féculents", "marque": "Taureau Ailé", "qualite_score": 9.0},
{"nom": "Riz long grain", "categorie": "Pâtes, riz et féculents", "marque": "Dari", "qualite_score": 8.4},
{"nom": "Couscous moyen", "categorie": "Pâtes, riz et féculents", "marque": "Dari", "qualite_score": 8.8},
{"nom": "Semoule fine", "categorie": "Pâtes, riz et féculents", "marque": "Tria", "qualite_score": 8.2},
{"nom": "Farine de blé", "categorie": "Pâtes, riz et féculents", "marque": "MayMouna", "qualite_score": 8.3},
{"nom": "Purée instantanée", "categorie": "Pâtes, riz et féculents", "marque": "Maggi", "qualite_score": 7.9},
{"nom": "Vermicelle", "categorie": "Pâtes, riz et féculents", "marque": "Panzani", "qualite_score": 8.0},
{"nom": "Nouilles instantanées", "categorie": "Pâtes, riz et féculents", "marque": "Indomie", "qualite_score": 8.5},

# 🥫 Conserves
{"nom": "Thon en boîte", "categorie": "Conserves", "marque": "Petit Navire", "qualite_score": 8.9},
{"nom": "Sardines à l’huile", "categorie": "Conserves", "marque": "Noura", "qualite_score": 8.4},
{"nom": "Maïs doux", "categorie": "Conserves", "marque": "Bonduelle", "qualite_score": 8.7},
{"nom": "Petits pois", "categorie": "Conserves", "marque": "Bonduelle", "qualite_score": 8.5},
{"nom": "Haricots rouges", "categorie": "Conserves", "marque": "Dari", "qualite_score": 8.0},
{"nom": "Tomate concentrée", "categorie": "Conserves", "marque": "Aicha", "qualite_score": 8.8},
{"nom": "Champignons émincés", "categorie": "Conserves", "marque": "Bonduelle", "qualite_score": 8.2},
{"nom": "Olives vertes", "categorie": "Conserves", "marque": "Tria", "qualite_score": 8.3},
{"nom": "Pois chiches", "categorie": "Conserves", "marque": "Dari", "qualite_score": 8.1},
{"nom": "Macédoine légumes", "categorie": "Conserves", "marque": "Bonduelle", "qualite_score": 7.9},

# 🫒 Huiles et vinaigres
{"nom": "Huile d’olive", "categorie": "Huiles et vinaigres", "marque": "Lesieur", "qualite_score": 9.2},
{"nom": "Huile de tournesol", "categorie": "Huiles et vinaigres", "marque": "Lesieur", "qualite_score": 8.6},
{"nom": "Huile de maïs", "categorie": "Huiles et vinaigres", "marque": "Cristal", "qualite_score": 8.4},
{"nom": "Vinaigre blanc", "categorie": "Huiles et vinaigres", "marque": "Star", "qualite_score": 7.8},
{"nom": "Vinaigre balsamique", "categorie": "Huiles et vinaigres", "marque": "Ponti", "qualite_score": 8.9},
{"nom": "Huile de colza", "categorie": "Huiles et vinaigres", "marque": "Lesieur", "qualite_score": 8.1},
{"nom": "Huile végétale", "categorie": "Huiles et vinaigres", "marque": "Cristal", "qualite_score": 8.0},
{"nom": "Vinaigre de cidre", "categorie": "Huiles et vinaigres", "marque": "Ponti", "qualite_score": 8.5},
{"nom": "Huile extra vierge", "categorie": "Huiles et vinaigres", "marque": "Terra Delyssa", "qualite_score": 9.3},
{"nom": "Sauce vinaigrette", "categorie": "Huiles et vinaigres", "marque": "Amora", "qualite_score": 7.7},

]

# =========================
# 📏 QUANTITÉS
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
    if "Pâtes" in categorie:
        return "500g"
    if "Conserves" in categorie:
        return "400g"
    if "Huiles" in categorie:
        return "1L"

    return "1 unité"

# =========================
# 💰 GÉNÉRATION PRIX
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
    
    if "Pâtes" in categorie:
        return random.uniform(4, 20)

    if "Conserves" in categorie:
        return random.uniform(5, 25)

    if "Huiles" in categorie:
        return random.uniform(10, 80)

    return random.uniform(5, 20)

# =========================
# 💰 OFFRES
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