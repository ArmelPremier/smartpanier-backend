import re
import unicodedata

def normalize_name(nom, quantite):

    texte = f"{nom} {quantite}"

    texte = texte.lower()

    texte = unicodedata.normalize(
        "NFKD",
        texte
    ).encode(
        "ascii",
        "ignore"
    ).decode()

    texte = re.sub(
        r"[^a-z0-9 ]",
        "",
        texte
    )

    return "_".join(texte.split())

KNOWN_BRANDS = [
    "Cigala",
    "Divella",
    "Panzani",
    "Fancy",
    "Ducros",
    "Hala",
    "Lio",
    "Star",
    "Sfassif"
]

def extract_brand(nom):

    for brand in KNOWN_BRANDS:

        if brand.lower() in nom.lower():
            return brand

    return None