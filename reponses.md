# Réponses — Exercice 1

> Brouillon : les passages entre [crochets] sont à remplacer par vos propres chiffres/observations après exécution sur le vrai corpus `docs/`. Relisez et reformulez avec vos mots.

## Q2 — Pourquoi conserver fichier, page et service ?

Ces métadonnées permettent de **citer la source** : l'assistant peut dire « d'après `teletravail.pdf`, page 2 », ce que le salarié peut vérifier lui-même, ce qui limite la confiance aveugle dans une réponse générée. Elles permettent aussi de **filtrer par service** : on peut restreindre la recherche aux documents RH ou IT (premier niveau de confidentialité) et améliorer la pertinence. Elles servent enfin à la maintenance : retrouver et réindexer les chunks d'un document modifié.

## Q4 — Avant/après nettoyage

[Coller ici l'affichage avant/après de `etape2_nettoyage.py`.]

Défaut restant : [ex. en-tête « Altéa Services — Document interne » répété sur chaque page / numéro de page « Page 2/5 » collé au texte].
Règle proposée : [ex. supprimer toute ligne qui apparaît sur plus de la moitié des pages d'un même document, ou `re.sub(r"^Page \d+(/\d+)?$", "", texte, flags=re.M)`].

## Q5 — Vérification à la main de `decouper("abcdefghij", 4, 1)`

Le pas d'avance est `taille - chevauchement = 3`.
- début 0 → `texte[0:4]` = `abcd`
- début 3 → `texte[3:7]` = `defg` (le `d` est repris)
- début 6 → `texte[6:10]` = `ghij` ; la fin (10) atteint la longueur du texte, on s'arrête.

Résultat : `["abcd", "defg", "ghij"]`.

## Q6 — Tableau (à remplir avec vos chiffres)

| Taille | Chevauchement | Nombre de chunks | Longueur moyenne |
|---|---|---|---|
| 200 | 20 | [ ] | [ ] |
| 500 | 50 | [ ] | [ ] |
| 1000 | 100 | [ ] | [ ] |

## Q7 — Choix de la taille

- **Chunk trop petit** : il perd son contexte (une phrase sans sa condition ou son exception), et la réponse est éparpillée sur plusieurs chunks ; de plus, le nombre de chunks (donc de vecteurs) augmente.
- **Chunk trop grand** : il mélange plusieurs sujets, son vecteur devient « flou » et la recherche est moins précise ; il consomme aussi plus de place dans le prompt du LLM.
- **Chevauchement** : il évite qu'une information coupée entre deux chunks soit perdue ; la fin d'un chunk est reprise au début du suivant.
- **Taille retenue** : [500 caractères / 50 de chevauchement, à justifier avec le tableau Q6 : compromis entre précision et contexte suffisant].

## Q8 — Dimension et volume

Le modèle `paraphrase-multilingual-MiniLM-L12-v2` produit des vecteurs de **384 dimensions** (`vecteurs.shape` donne `(3, 384)`).
Nombre de valeurs à stocker = nombre de chunks × 384 = [N chunks] × 384 = [résultat].

## Q9 — Matrice de similarité

[Coller la matrice.] Les phrases 1 et 2 (congé / vacances) sont proches ; la phrase 3 (VPN) est éloignée des deux autres.
Les phrases 1 et 2 ont presque aucun mot en commun mais **le même sens** : le modèle d'embedding est entraîné à placer dans des zones voisines de l'espace des textes de sens proche (« congé » ≈ « vacances », « poser » ≈ « demander »). La recherche est donc **sémantique** et non par mots-clés.

## Q12 — Relance de l'indexation

Le nombre de chunks **ne double pas** : [vérifier, ex. 112 puis 112]. `upsert` met à jour un chunk dont l'`id` existe déjà et n'ajoute que les nouveaux, alors que `add` ajouterait des doublons ou provoquerait des erreurs d'identifiants. Le script est ainsi rejouable sans risque.
Quand un document est modifié : il faut **réindexer** ce document ; l'`upsert` met à jour les chunks de mêmes ids, mais si le document est devenu plus court, les anciens chunks en trop restent : il faut d'abord **supprimer** les chunks de cette source (`collection.delete(where={"source": "nom.pdf"})`) puis les réinsérer (ou reconstruire toute la base).

## Q13 — Pourquoi pas `base_vectorielle/` sur GitHub ?

C'est un **artefact généré**, volumineux, binaire, qui change à chaque indexation et qui est entièrement reproductible depuis le code et les documents. Le versionner alourdirait le dépôt et créerait des conflits inutiles.
Un collègue clone le dépôt, crée un environnement (`python -m venv .venv`, `pip install -r requirements.txt`), puis lance `python etape4_indexation.py` : cela relit les documents, les nettoie, les découpe et recrée la base.
