# etape5_recherche.py
import chromadb
from sentence_transformers import SentenceTransformer

modele = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
collection = chromadb.PersistentClient(
    path="base_vectorielle").get_collection("altea")


def rechercher(question, k=3, service=None):
    vecteur = modele.encode([question]).tolist()
    filtre = {"service": service} if service else None
    res = collection.query(query_embeddings=vecteur,
                           n_results=k, where=filtre)
    resultats = []
    for texte, meta, distance in zip(res["documents"][0],
                                     res["metadatas"][0], res["distances"][0]):
        resultats.append({
            "texte": texte,
            "source": meta["source"],
            "page": meta["page"],
            "service": meta["service"],
            "score": 1 - distance,
        })
    return resultats


def afficher(resultats):
    for r in resultats:
        print(f"  [{r['service']}] {r['source']} p.{r['page']}  "
              f"score={r['score']:.3f}")


if __name__ == "__main__":
    # Q1 : 3 questions de salariés
    for q in ["Combien de jours de télétravail par semaine ?",
              "Comment réinitialiser mon mot de passe ?",
              "Quel est le plafond de remboursement d'un repas d'affaires ?"]:
        print("\n###", q)
        afficher(rechercher(q))

    # Q2 : effet de k sur une même question
    q = "Comment poser un jour de congé ?"
    for k in (1, 3, 10):
        print(f"\n### k = {k} : {q}")
        afficher(rechercher(q, k=k))

    # Q3 : filtre par service
    q = "Quelle est la procédure pour les congés ?"
    for service in ("RH", "IT"):
        print(f"\n### service = {service} : {q}")
        afficher(rechercher(q, service=service))