import json
import re
from pathlib import Path
from unidecode import unidecode
import hashlib


# =====================================================
# CONFIGURATION
# =====================================================

KNOWN_BRANDS = {
    "fancy",
    "ducros",
    "serano",
    "sfassif",
    "hala",
    "star",
    "zaytouni",
    "olinia",
    "panzani",
    "jessy's",
    "jessys",
    "bjorg",
    "tipiak",
    "sundari",
    "cigala",
    "ebly",
    "denia",
    "rosana",
    "cerebos",
    "gemignani",
    "al badr",
    "alesto",
    "goldy",
    "delcielo",
    "pikarome",
    "mido",
    "divella",
    "alhora",
    "ja"
}

BRAND_PATTERNS = [
    (brand, re.compile(rf"\b{re.escape(unidecode(brand.lower()))}\b"))
    for brand in KNOWN_BRANDS
]


STOPWORDS = {
    "de","du","des","d",
    "et","au","aux",
    "la","le","les",
    "en","avec","pour","sur",

    "boite",
    "bouteille",
    "verre",
    "chef",
    "courant",
    "gout",
    "kg",
    "grillees",
    "grillee"
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

    # suppression marques
    for brand in KNOWN_BRANDS:
        name = name.replace(brand, " ")

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

    for brand in KNOWN_BRANDS:
        name = name.replace(brand, " ")

    name = QUANTITY_PATTERN.sub(" ", name)

    name = re.sub(r"[^a-z0-9 ]", " ", name)

    words = []

    for w in name.split():

        if w in STOPWORDS:
            continue

        w = SINGULAR_MAP.get(w, w)

        words.append(w)

        words = list(dict.fromkeys(words))

    return " ".join(words)


def generate_product_key(product):

    text = (
        product["nom_normalise"]
        + "_"
        + str(product["categorie_canonique"])
    )

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