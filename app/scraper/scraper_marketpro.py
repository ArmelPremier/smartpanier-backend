import requests
import json
import re


CATEGORY_URLS = [
    # Page 1
    "https://marketpro.ma/product-category/epicerie/fruits-secs/",
    "https://marketpro.ma/product-category/epicerie/conserves/",
    "https://marketpro.ma/product-category/epicerie/epices/",
    "https://marketpro.ma/product-category/epicerie/huilevinaigre/",
    "https://marketpro.ma/product-category/epicerie/pates-et-riz/",
    # Page 2
    "https://marketpro.ma/product-category/epicerie/fruits-secs/page/2/",
    "https://marketpro.ma/product-category/epicerie/conserves/page/2/",
    "https://marketpro.ma/product-category/epicerie/epices/page/2/",
    "https://marketpro.ma/product-category/epicerie/huilevinaigre/page/2/",
    "https://marketpro.ma/product-category/epicerie/pates-et-riz/page/2/",
]

HEADERS = {
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}


def extract_quantite(text):

    text = text.upper()

    patterns = [
        r'(\d+[.,]?\d*\s?KG)',
        r'(\d+[.,]?\d*\s?G)',
        r'(\d+[.,]?\d*\s?L)',
        r'(\d+[.,]?\d*\s?ML)',
        r'(\d+[.,]?\d*\s?CL)'
    ]

    for pattern in patterns:
        match = re.search(pattern, text)

        if match:
            return match.group(1)

    if "AU KG" in text or text.endswith("KG"):
        return "1 KG"

    return "1 unité"

def detect_category(url):

    if "fruits-secs" in url:
        return "Fruits secs"

    if "conserves" in url:
        return "Conserves"

    if "epices" in url:
        return "Épices"

    if "huilevinaigre" in url:
        return "Huiles"

    if "pates-et-riz" in url:
        return "Pâtes et Riz"

    return "Autres"


def extract_products_array(html):
    start_marker = '"products":['
    start_idx = html.find(start_marker)
    if start_idx == -1:
        return None
    bracket_start = start_idx + len(start_marker) - 1
    depth = 0
    i = bracket_start
    while i < len(html):
        if html[i] == '[':
            depth += 1
        elif html[i] == ']':
            depth -= 1
            if depth == 0:
                return html[bracket_start:i+1]
        i += 1
    return None


all_products = []
seen = set()

for url in CATEGORY_URLS:

    print("\nPAGE :", url)

    response = requests.get(
        url,
        headers=HEADERS
    )

    html = response.text

    products_json = extract_products_array(html)

    if not products_json:
        print("JSON INTROUVABLE")
        continue

    print("JSON PRODUITS TROUVÉ")

    products_data = json.loads(products_json)

    print("Produits JSON :", len(products_data))

    for item in products_data:

        nom = item.get("title") or item.get("item_name") or item.get("name")
        if not nom:
            print("CLÉS DISPO :", list(item.keys()))
            continue

        # Format GA4 : price direct / Format ancien : prices.price / 100
        if "price" in item:
            try:
                prix = float(item["price"])
            except (ValueError, TypeError):
                continue
        elif "prices" in item and isinstance(item["prices"], dict):
            prix = item["prices"]["price"] / 100
        else:
            print("PRIX INTROUVABLE, clés :", list(item.keys()))
            continue

        produit = {
            "nom": nom,
            "prix": prix,
            "quantite": extract_quantite(nom),
            "categorie": detect_category(url),
            "magasin": "MarketPro"
        }

        if nom not in seen:
            seen.add(nom)
            all_products.append(produit)

    

with open(
    "marketpro_products.json",
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

with open("debug_marketpro.html", "w", encoding="utf-8") as f:
    f.write(response.text)