# Réponses — Exercice 1

## Résultats des questions de code

- **Q1** : 23 pages lues pour 15 documents. Les 9 PDF ont 2 pages chacun (18 pages) et les 5 fichiers `.txt` ont 1 page chacun (5 pages).
- **Q3** : 23 pages avant nettoyage, 23 pages après. Aucune page n'est devenue vide, il n'y a donc rien à supprimer.
- **Q10** : 23 pages donnent 69 chunks produits (taille 500, chevauchement 50) ; 69 chunks sont indexés. Le contrôle `chunks indexés == chunks produits` passe.
- **Q11** : pour chaque question, le premier résultat est dans le bon document (`teletravail.pdf`, `mot_de_passe.txt`, `notes_de_frais.pdf`), avec des distances cosinus de 0,32, 0,30 et 0,41.

## Q2 — Pourquoi conserver le fichier, la page et le service ?

Conserver ces métadonnées permet d'abord de **citer la source** : l'assistant peut répondre « d'après `teletravail.pdf`, page 1 », et le salarié peut vérifier lui-même l'information, ce qui évite de se fier aveuglément à une réponse générée. Cela permet ensuite de **filtrer par service** : on peut restreindre la recherche aux documents RH ou IT, ce qui améliore la pertinence et constitue un premier niveau de confidentialité. Enfin, les métadonnées servent à la maintenance : retrouver et réindexer les chunks d'un document modifié.

## Q4 — Avant/après nettoyage

Page `horaires.txt` (affichée tronquée), avant puis après `nettoyer` :

```
AVANT : "HORAIRES D'OUVERTURE DES SITES\nAltéa Services — Services généraux — Référence GEN-004 — mise à jour du 1er septembre 2026\n\n1. Horaires des sites\nSite de Paris (siège) : ouvert du lundi au vendredi de 7 h à 20 h. ..."
APRÈS : "HORAIRES D'OUVERTURE DES SITES\nAltéa Services — Services généraux — Référence GEN-004 — mise à jour du 1er septembre 2026\n\n1. Horaires des sites\nSite de Paris (siège) : ouvert du lundi au vendredi de 7 h à 20 h. ..."
```

Le texte est identique avant et après : cette page, issue d'un fichier `.txt`, ne contenait ni espaces en trop, ni sauts de ligne multiples, ni mot coupé. Le nettoyage n'a donc rien eu à corriger ici.

**Défaut qui reste :** dans les PDF, un en-tête et un pied de page se répètent et se retrouvent dans les chunks. La recherche de la question sur les frais de déplacement a retourné un chunk de `notes_de_frais.pdf` qui contient « Altéa Services — Document interne — Diffusion restreinte », le numéro de page « 1 » et « Document fictif réalisé à des fins pédagogiques ». Ce bruit n'a aucun lien avec la question mais entre dans le vecteur du chunk et peut le faire remonter à tort.

**Règle proposée :** supprimer ces lignes avec des expressions régulières dans `nettoyer`, par exemple `re.sub(r"^Altéa Services — Document interne.*$", "", texte, flags=re.M)` pour l'en-tête, `re.sub(r"^\d+$", "", texte, flags=re.M)` pour une ligne ne contenant qu'un numéro de page, et `re.sub(r"^Document fictif.*$", "", texte, flags=re.M)` pour le pied de page. Plus généralement, on peut supprimer toute ligne qui apparaît sur plusieurs pages d'un même document.

## Q5 — Vérification à la main de `decouper("abcdefghij", taille=4, chevauchement=1)`

Le pas d'avance est `taille - chevauchement = 3`.
- début 0 : `texte[0:4]` donne `abcd`.
- début 3 : `texte[3:7]` donne `defg` (le `d` est repris du morceau précédent).
- début 6 : `texte[6:10]` donne `ghij` ; la fin (10) atteint la longueur du texte, on s'arrête.

Résultat : `["abcd", "defg", "ghij"]`, ce que le script confirme.

## Q6 — Tableau des trois tailles

| Taille (caractères) | Chevauchement | Nombre de chunks | Longueur moyenne |
|---|---|---|---|
| 200 | 20 | 156 | 189 |
| 500 | 50 | 69 | 423 |
| 1000 | 100 | 38 | 746 |

## Q7 — Choix de la taille

- **Chunk trop petit :** il perd son contexte (une règle sans sa condition ou son exception) et l'information est éparpillée sur plusieurs chunks. Le nombre de chunks, donc de vecteurs à calculer et à stocker, augmente (156 chunks à 200 caractères contre 69 à 500).
- **Chunk trop grand :** il mélange plusieurs sujets, son vecteur devient moins précis et la recherche est moins fine. Il prend aussi plus de place dans le prompt envoyé au LLM.
- **Chevauchement :** il évite de perdre une information coupée entre deux chunks, car la fin d'un chunk est reprise au début du suivant.
- **Taille retenue :** 500 caractères avec 50 de chevauchement. Cela donne 69 chunks d'environ 420 caractères, soit à peu près un paragraphe ou une section courte, un compromis entre précision de la recherche et contexte suffisant pour répondre.

## Q8 — Dimension et volume

Le modèle `paraphrase-multilingual-MiniLM-L12-v2` produit des vecteurs de **384 dimensions** (`vecteurs.shape` affiche `(3, 384)`). Avec la taille retenue, il y a 69 chunks, donc 69 × 384 = **26 496 nombres** à stocker pour tout le corpus.

## Q9 — Matrice de similarité

```
tensor([[ 1.0000,  0.4888, -0.0353],
        [ 0.4888,  1.0000, -0.0020],
        [-0.0353, -0.0020,  1.0000]])
```

Les phrases 1 (« Comment poser un jour de congé ? ») et 2 (« Quelle est la procédure pour demander des vacances ? ») sont proches, avec une similarité de 0,49. La phrase 3 (« Mon ordinateur ne se connecte pas au VPN. ») est éloignée des deux autres, avec une similarité proche de 0.

Les phrases 1 et 2 n'ont presque aucun mot en commun, mais elles ont le **même sens**. Le modèle d'embedding est entraîné à placer des textes de sens voisin dans des zones proches de l'espace des vecteurs (« congé » proche de « vacances », « poser » proche de « demander »). La recherche est donc **sémantique** et non basée sur les mots-clés.

## Q12 — Relance de l'indexation

Après une seconde exécution du script, le nombre de chunks reste à **69** : il ne double pas. `upsert` met à jour un chunk dont l'identifiant existe déjà et n'ajoute que les nouveaux, alors que `add` créerait des doublons ou provoquerait des erreurs d'identifiants. Le script d'indexation peut ainsi être relancé sans risque.

Le jour où un document est modifié, il faut le **réindexer**. L'`upsert` met à jour les chunks qui gardent les mêmes identifiants, mais si le document est devenu plus court, les anciens chunks en trop resteraient dans la base. Il faut donc d'abord **supprimer** les chunks de cette source (`collection.delete(where={"source": "nom.pdf"})`), puis les réinsérer, ou reconstruire toute la base.

## Q13 — Pourquoi `base_vectorielle/` n'est-il pas envoyé sur GitHub ?

C'est un **artefact généré** : volumineux, binaire, modifié à chaque indexation et entièrement reproductible à partir du code et des documents. Le versionner alourdirait le dépôt et créerait des conflits inutiles.

Un collègue qui clone le dépôt crée un environnement (`python -m venv .venv`, puis `pip install -r requirements.txt`), puis lance `python etape4_indexation.py` : le script relit les documents, les nettoie, les découpe et recrée la base vectorielle.
