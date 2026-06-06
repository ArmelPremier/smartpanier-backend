import requests
from bs4 import BeautifulSoup
import json
import re

CATEGORY_URLS = [
    "https://www.mymarket.ma/collections/fruits-secs",
    "https://www.mymarket.ma/collections/epices?page=2",
    "https://www.mymarket.ma/collections/huiles-et-vinaigres",
    "https://www.mymarket.ma/collections/pates?page=2",
    "https://www.mymarket.ma/collections/riz",
    "https://www.mymarket.ma/collections/conserves"
]

HEADERS = {
    "User-Agent":
    "Mozilla/5.0"
}

def extract_quantite(text):

    patterns = [
        r'(\d+[.,]?\d*\s?KG)',
        r'(\d+[.,]?\d*\s?G)',
        r'(\d+[.,]?\d*\s?L)',
        r'(\d+[.,]?\d*\s?ML)',
        r'(\d+[.,]?\d*\s?CL)'
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text.upper()
        )

        if match:
            return match.group(1)

    return "1 unité"

def detect_category(url):

    if "fruits-secs" in url:
        return "Fruits secs"

    if "epices" in url:
        return "Épices"

    if "huiles" in url:
        return "Huiles"

    if "pates" in url:
        return "Pâtes"

    if "riz" in url:
        return "Riz"

    if "conserves" in url:
        return "Conserves"

    return "Autres"

all_products = []
seen = set()

for url in CATEGORY_URLS:

    print("\nPAGE :", url)

    response = requests.get(
        url,
        headers=HEADERS
    )

    soup = BeautifulSoup(
        response.text,
        "lxml"
    )

    cards = soup.find_all(
        "product-card",
        class_="card card-product"
    )

    print(
        "Produits trouvés :",
        len(cards)
    )

    for card in cards:

        nom_tag = card.find(
            "h2",
            class_="card-heading"
        )

        prix_tag = card.find(
            "span",
            class_="price-item"
        )

        if not nom_tag or not prix_tag:
            continue

        nom = nom_tag.get_text(
            strip=True
        )

        prix_text = prix_tag.get_text(
            strip=True
        )

        prix_text = prix_text.replace(
            "dh",
            ""
        )

        prix_text = prix_text.replace(
            "ttc",
            ""
        )

        prix_text = prix_text.replace(
            ",",
            ""
        )

        try:
            prix = float(prix_text.strip())
        except ValueError:
            continue

        if prix <= 0 or prix > 5000:
            continue

        if nom in seen:
            continue

        seen.add(nom)

        produit = {
            "nom": nom,
            "prix": prix,
            "quantite": extract_quantite(nom),
            "categorie": detect_category(url),
            "magasin": "MyMarket"
        }

        all_products.append(
            produit
        )

with open(
    "mymarket_products.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        all_products,
        f,
        ensure_ascii=False,
        indent=4
    )

print(
    "\nTOTAL :",
    len(all_products)
)