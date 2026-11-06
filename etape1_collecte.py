# etape1_collecte.py
from collections import Counter
from pathlib import Path

from pypdf import PdfReader


def lire_pdf(chemin):
    lecteur = PdfReader(chemin)
    pages = []
    for numero, page in enumerate(lecteur.pages, start=1):
        texte = page.extract_text() or ""  # extract_text peut renvoyer None/"" sur une page image
        pages.append({"source": chemin.name, "page": numero, "texte": texte})
    return pages


def lire_txt(chemin):
    texte = Path(chemin).read_text(encoding="utf-8")
    return [{"source": chemin.name, "page": 1, "texte": texte}]


def collecter(dossier="docs"):
    pages = []
    for chemin in sorted(Path(dossier).rglob("*")):
        service = chemin.parent.name  # RH, IT ou General
        if chemin.suffix.lower() == ".pdf":
            lues = lire_pdf(chemin)
        elif chemin.suffix.lower() == ".txt":
            lues = lire_txt(chemin)
        else:
            continue  # dossiers et autres types de fichiers ignorés
        for p in lues:
            p["service"] = service
            pages.append(p)
    return pages


if __name__ == "__main__":
    pages = collecter()
    print(len(pages), "pages lues")

    # Q1 : nombre de pages lues pour chaque document
    par_doc = Counter((p["service"], p["source"]) for p in pages)
    for (service, source), n in sorted(par_doc.items()):
        print(f"  {service:8} {source:45} {n} page(s)")
