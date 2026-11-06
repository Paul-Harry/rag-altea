# etape2_nettoyage.py
import re

from etape1_collecte import collecter


def nettoyer(texte):
    texte = re.sub(r"[ \t]+", " ", texte)                            # plusieurs espaces -> un seul
    texte = re.sub(r"^Altéa Services — Document interne.*$", "", texte, flags=re.M)  # en-tête répété
    texte = re.sub(r"^Document fictif réalisé.*$", "", texte, flags=re.M)             # pied de page
    texte = re.sub(r"^\d{1,2}\s*$", "", texte, flags=re.M)                            # numéro de page seul
    texte = re.sub(r"\n{3,}", "\n\n", texte)                         # 3 sauts de ligne ou plus -> 2
    texte = re.sub(r"-\n(\w)", r"\1", texte)                         # recoller les mots coupés
    return texte.strip()


def nettoyer_pages(pages):
    """Q3 : nettoie toutes les pages et supprime celles qui deviennent vides."""
    propres = []
    for p in pages:
        texte = nettoyer(p["texte"])
        if texte:
            propres.append({**p, "texte": texte})
    return propres


if __name__ == "__main__":
    pages = collecter()
    propres = nettoyer_pages(pages)
    print(len(pages), "pages lues ->", len(propres), "pages après nettoyage")

    # Q4 : une même page avant / après nettoyage
    brutes = {(p["source"], p["page"]): p["texte"] for p in pages}
    exemple = propres[0]
    print("\n===== AVANT =====")
    print(repr(brutes[(exemple["source"], exemple["page"])][:600]))
    print("\n===== APRÈS =====")
    print(repr(exemple["texte"][:600]))
