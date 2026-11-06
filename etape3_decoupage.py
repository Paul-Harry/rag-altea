# etape3_decoupage.py
from etape1_collecte import collecter
from etape2_nettoyage import nettoyer_pages


def decouper(texte, taille=500, chevauchement=50):
    assert chevauchement < taille, "le chevauchement doit être plus petit que la taille"
    morceaux = []
    debut = 0
    while debut < len(texte):
        fin = debut + taille                      # fin du morceau
        morceaux.append(texte[debut:fin])
        if fin >= len(texte):
            break
        debut = fin - chevauchement               # avancer en gardant le chevauchement
    return morceaux


def decouper_pages(pages, taille=500, chevauchement=50):
    chunks = []
    for p in pages:
        for i, morceau in enumerate(decouper(p["texte"], taille, chevauchement)):
            chunks.append({
                "id": f"{p['source']}-p{p['page']}-{i}",
                "texte": morceau,
                "source": p["source"],
                "page": p["page"],
                "service": p["service"],
            })
    return chunks


if __name__ == "__main__":
    # Q5 : vérification demandée par le sujet
    attendu = ["abcd", "defg", "ghij"]
    obtenu = decouper("abcdefghij", taille=4, chevauchement=1)
    print(obtenu, "OK" if obtenu == attendu else "ERREUR")
    assert obtenu == attendu

    # Q6 : tableau pour trois tailles
    pages = nettoyer_pages(collecter())
    print("\n| Taille | Chevauchement | Nombre de chunks | Longueur moyenne |")
    print("|---|---|---|---|")
    for taille, chev in [(200, 20), (500, 50), (1000, 100)]:
        chunks = decouper_pages(pages, taille, chev)
        moyenne = sum(len(c["texte"]) for c in chunks) / len(chunks)
        print(f"| {taille} | {chev} | {len(chunks)} | {moyenne:.0f} |")
