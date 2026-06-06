import json
import re
from pathlib import Path
from unidecode import unidecode
import hashlib


# =====================================================
# CONFIGURATION
# =====================================================

KNOWN_BRANDS = {
    # Marques MyMarket
    "fancy", "ducros", "serano", "sfassif", "hala", "zaytouni", "olinia",
    "panzani", "jessys", "bjorg", "tipiak", "sundari", "cigala", "ebly",
    "denia", "rosana", "cerebos", "gemignani", "alesto", "ja",
    "madila", "sifa", "carle", "joly", "gaya", "ayala", "harmony",
    "barilla", "uncle", "bens", "caprice", "baleine", "beros",
    # Marques MarketPro
    "alhora", "borges", "lesieur", "kania", "cevital", "camelia",
    "lio", "louza", "dessaux", "ideal", "fritys", "frity",
    "delcielo", "goldy", "pikarome", "mido", "divella",
    "al badr", "alesto", "star",
    # Marques thon MarketPro
    "tamima", "caly", "chellah",
    # Autres marques MarketPro
    "savora", "oncle", "siof", "bangor", "aicha",
    "kasbah", "perla", "eurogold", "leduc",
}

BRAND_PATTERNS = [
    (brand, re.compile(rf"\b{re.escape(unidecode(brand.lower()))}\b"))
    for brand in KNOWN_BRANDS
]


STOPWORDS = {
    # Particules françaises
    "de","du","des","d","et","au","aux","la","le","les","en","avec","pour","sur","a",
    # Contenant / packaging
    "boite","bouteille","verre","sachet","pot","bidon","brique","pack","kg",
    # Mots génériques déjà dans KNOWN_BRANDS ou inutiles
    "chef","courant","gout","grillees","grillee","conserve",
    # Méthodes de préparation
    "grille","sale","seche","fume","moulu","moulee","entier","entiere",
    "taille","coupe","hache","hachee","emiette","emince",
    "tranche",           # champignons tranchés
    "filet",             # thon filet → thon (après CORRECTIONS: filets→filet)
    "bonite",            # thon caly bonite → thon (type de thon)
    # Descripteurs de qualité
    "vierge","extra","pur","pure","naturel","naturelle","premium",
    "bio","frais","fraiche","special","select","royal","gold",
    "surchoix",          # huile de table surchoix → huile de table
    # Types/sous-types de pâtes
    "rigate",            # penne rigate → penne
    "mini",              # mini penne / mini farfalle → penne / farfalle
    # Types de riz
    "risotto",           # riz risotto → riz
    "rouge",             # riz cigala rouge → riz (couleur packaging)
    "etuve",             # riz étuvé → riz
    # Autres
    "grains","grain","dore","doree","secs","sec",
    "vegetale",          # huile végétale (descripteur générique)
}


CORRECTIONS = {
    "salees": "sale",
    "salee": "sale",
    "fumees": "fume",
    "fumee": "fume",
    "grillees": "grille",
    "grillee": "grille",
    "sechees": "seche",
    "sechee": "seche",
    # Pluriels/accords → forme canonique (pour STOPWORDS)
    "tranches": "tranche",
    "tranchees": "tranche",
    "tranchee": "tranche",
    "rouges": "rouge",
    "filets": "filet",
}




SINGULAR_MAP = {
    "figues": "figue",
    "abricots": "abricot",
    "dattes": "datte",
    "amandes": "amande",
    "pistaches": "pistache",
    "raisins": "raisin",
    "cerises": "cerise",
    "cacahuetes": "cacahuete",
    "noix": "noix"
}

QUANTITY_PATTERN = re.compile(
    r"\d+[,.]?\d*\s*(kg|g|gr|grs|l|ml|cl)\b"
)


# =====================================================
# UTILITAIRES
# =====================================================

def clean_text(text: str) -> str:

    text = unidecode(text.lower())
    text = text.strip()
    text = re.sub(r"\s+", " ", text)

    for old, new in CORRECTIONS.items():
        text = text.replace(old, new)

    return text

CATEGORY_MAPPING = {
    "pates": "feculents",
    "riz": "feculents",
    "pates et riz": "feculents",
    "conserves": "conserves",
}



# =====================================================
# MARQUE
# =====================================================

def extract_brand(product_name):

    name = clean_text(product_name)

    for brand, pattern in BRAND_PATTERNS:
        if pattern.search(name):
            return brand.title()

    return None


# =====================================================
# QUANTITE
# =====================================================

def normalize_quantity(quantity):

    if not quantity:
        return None

    q = clean_text(str(quantity))

    if "1/2l" in q or "1/2 l" in q:
        return 500

    m = re.search(r"(\d+[,.]?\d*)", q)

    if not m:
        return None

    value = float(m.group(1).replace(",", "."))

    if "kg" in q:
        return round(value * 1000)

    if "g" in q:
        return round(value)

    if "cl" in q:
        return round(value * 10)

    if "ml" in q:
        return round(value)

    if "l" in q:
        return round(value * 1000)
    
    if "unite" in q:
        return None

    return round(value)


# =====================================================
# CODE NORMALISE
# =====================================================

def normalize_code(name):

    name = clean_text(name)

    # Word-boundary matching
    for _, pattern in BRAND_PATTERNS:
        name = pattern.sub(" ", name)

    # suppression fractions
    name = re.sub(r"\b1/2\s*(l|kg)\b", " ", name)

    # suppression quantités
    name = QUANTITY_PATTERN.sub(" ", name)

    name = re.sub(r"[^a-z0-9 ]", " ", name)
    

    words = []

    for word in name.split():

        if word in STOPWORDS:
            continue

        word = SINGULAR_MAP.get(word, word)

        if len(word) < 2:
            continue

        words.append(word)



    # tri alphabétique
    words = list(dict.fromkeys(words))

    return "_".join(words)


# =====================================================
# QUALITE
# =====================================================

def quality_score(name):

    name = clean_text(name)

    keywords = {
        "bio": 2,
        "extra": 1,
        "vierge": 1,
        "premium": 2,
        "deluxe": 2,
        "sans gluten": 1,
        "quinoa": 1,
        "truffe": 2,
        "fumee": 1,
        "fumees": 1,
    }

    score = 5

    for keyword, bonus in keywords.items():
        if keyword in name:
            score += bonus

    return min(score, 10)


# =====================================================
# TRAITEMENT
# =====================================================

def process_file(input_file, output_file):

    with open(input_file, "r", encoding="utf-8") as f:
        products = json.load(f)

    for product in products:

        product["marque"] = extract_brand(
            product["nom"]
        )

        product["code_normalise"] = normalize_code(
            product["nom"]
        )

        product["qualite_score"] = quality_score(
            product["nom"]
        )

        product["quantite_normalisee"] = normalize_quantity(
            product.get("quantite")
        )

        categorie = clean_text(product["categorie"])

        product["categorie_canonique"] = CATEGORY_MAPPING.get(
            categorie,
            categorie
        )

        product["nom_normalise"] = normalize_name(
            product["nom"]
        )

        product["product_key"] = generate_product_key(
            product
        )

        product["cleaning_confidence"] = cleaning_confidence(
            product
        )

        product["matching_tokens"] = sorted(
            set(product["nom_normalise"].split())
        )

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(
            products,
            f,
            ensure_ascii=False,
            indent=4
        )

def normalize_name(name):

    name = clean_text(name)

    # Word-boundary matching (évite "hala" dans "halabi", etc.)
    for _, pattern in BRAND_PATTERNS:
        name = pattern.sub(" ", name)

    name = QUANTITY_PATTERN.sub(" ", name)
    name = re.sub(r"[^a-z0-9 ]", " ", name)

    words = []

    for w in name.split():
        if w in STOPWORDS:
            continue
        if len(w) < 2:
            continue
        if any(c.isdigit() for c in w):
            # Filtre les codes numériques : "ndeg5", "4", "3x", "100"
            continue
        w = SINGULAR_MAP.get(w, w)
        words.append(w)
        words = list(dict.fromkeys(words))

    return " ".join(words)


def generate_product_key(product):

    nom = product["nom_normalise"]
    if not nom:
        # Fallback si la normalisation a tout supprimé (ex: "Cigala Rouge 5KG")
        nom = clean_text(product["nom"])[:40]

    text = nom + "_" + str(product["categorie_canonique"])

    return hashlib.md5(
        text.encode()
    ).hexdigest()[:12]

def cleaning_confidence(product):

    score = 100

    if not product["code_normalise"]:
        score -= 30

    if not product["categorie_canonique"]:
        score -= 20

    if len(product["nom_normalise"].split()) < 2:
        score -= 15

    if not product["quantite_normalisee"]:
        score -= 10

    return max(score, 0)
    

# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    BASE_DIR = Path(__file__).resolve().parent.parent
    SCRAPER_DIR = BASE_DIR / "scraper"
    DATA_DIR = BASE_DIR.parent / "data"

    process_file(
        SCRAPER_DIR / "marketpro_products.json",
        DATA_DIR / "marketpro_products_clean.json"
    )

    process_file(
        SCRAPER_DIR / "mymarket_products.json",
        DATA_DIR / "mymarket_products_clean.json"
    )

    

    print("Produits nettoyés avec succès")