# etape7_evaluation.py
import csv

from etape5_recherche import rechercher


def taux_reussite(fichier="evaluation.csv", k=3):
    with open(fichier, encoding="utf-8") as f:
        lignes = list(csv.DictReader(f))
    trouves = 0
    for ligne in lignes:
        sources = [r["source"] for r in rechercher(ligne["question"], k)]
        if ligne["document_attendu"] in sources:  # le bon document est-il trouvé ?
            trouves += 1
    return trouves / len(lignes)


def generer_reponses(fichier="evaluation.csv", sortie="reponses_generees.csv", k=3):
    from etape6_generation import repondre
    with open(fichier, encoding="utf-8") as f:
        lignes = list(csv.DictReader(f))
    with open(sortie, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["question", "document_attendu", "reponse", "sources",
                    "note", "sources_exactes"])  # les 2 dernières colonnes : à remplir à la main
        for ligne in lignes:
            reponse, extraits = repondre(ligne["question"], k)
            sources = "; ".join(f"{e['source']} p.{e['page']}" for e in extraits)
            w.writerow([ligne["question"], ligne["document_attendu"], reponse, sources, "", ""])
            print("ok :", ligne["question"])


if __name__ == "__main__":
    for k in (1, 3, 5):
        print(f"k = {k} : {taux_reussite(k=k):.0%} "
              "de questions où le bon document est trouvé")