# etape4_indexation.py
# Usage :
#   python etape4_indexation.py demo       -> partie A : découvrir les embeddings (Q8, Q9)
#   python etape4_indexation.py            -> partie B : indexer tout le corpus (Q10, Q12)
#   python etape4_indexation.py recherche  -> premières recherches (Q11)
import sys

import chromadb
from sentence_transformers import SentenceTransformer, util

from etape1_collecte import collecter
from etape2_nettoyage import nettoyer_pages
from etape3_decoupage import decouper_pages

MODELE = "paraphrase-multilingual-MiniLM-L12-v2"
TAILLE = 500           # à confirmer après Q6/Q7
CHEVAUCHEMENT = 50
DOSSIER_BASE = "base_vectorielle"


# ---------- Partie A : découvrir les embeddings ----------
def demo_embeddings():
    modele = SentenceTransformer(MODELE)
    phrases = [
        "Comment poser un jour de congé ?",
        "Quelle est la procédure pour demander des vacances ?",
        "Mon ordinateur ne se connecte pas au VPN.",
    ]
    vecteurs = modele.encode(phrases)
    print(vecteurs.shape)                       # (3, 384) -> dimension du vecteur (Q8)
    print(util.cos_sim(vecteurs, vecteurs))     # matrice de similarité (Q9)


# ---------- Partie B : indexation ----------
def indexer():
    modele = SentenceTransformer(MODELE)

    # Étapes 1 à 3 enchaînées
    pages = nettoyer_pages(collecter())
    chunks = decouper_pages(pages, TAILLE, CHEVAUCHEMENT)
    print(len(pages), "pages ->", len(chunks), "chunks produits")

    # Étape 4
    client = chromadb.PersistentClient(path=DOSSIER_BASE)
    collection = client.get_or_create_collection("altea", metadata={"hnsw:space": "cosine"})

    textes = [c["texte"] for c in chunks]
    vecteurs = modele.encode(textes, show_progress_bar=True).tolist()

    collection.upsert(
        ids=[c["id"] for c in chunks],
        documents=textes,
        embeddings=vecteurs,
        metadatas=[{"source": c["source"], "page": c["page"], "service": c["service"]}
                   for c in chunks],
    )
    print(collection.count(), "chunks indexés")

    # Q10 : contrôle
    assert collection.count() == len(chunks), "chunks indexés != chunks produits"
    print("OK : chunks indexés == chunks produits")
    return collection


# ---------- Q11 : premières recherches ----------
QUESTIONS = [
    "Combien de jours de télétravail ?",
    "J'ai oublié mon mot de passe, que faire ?",
    "Comment me faire rembourser mes frais de déplacement ?",
]


def recherche_test():
    modele = SentenceTransformer(MODELE)
    collection = chromadb.PersistentClient(path=DOSSIER_BASE).get_collection("altea")
    for question in QUESTIONS:
        resultat = collection.query(
            query_embeddings=modele.encode([question]).tolist(), n_results=3)
        print("\n###", question)
        for doc, meta, dist in zip(resultat["documents"][0],
                                   resultat["metadatas"][0],
                                   resultat["distances"][0]):
            print(f"  [{meta['service']}] {meta['source']} p.{meta['page']}  "
                  f"distance={dist:.3f}\n    {doc[:150]!r}")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "index"
    {"demo": demo_embeddings, "index": indexer, "recherche": recherche_test}[mode]()
