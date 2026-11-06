# etape6_generation.py
from openai import OpenAI

from etape5_recherche import rechercher

client = OpenAI(base_url="http://localhost:11434/v1",
                api_key="ollama")  # Ollama en local
MODELE = "gemma3:1b"
REPLI = "Je ne trouve pas cette information dans la documentation."


def construire_prompt(question, extraits):
    contexte = ""
    for i, e in enumerate(extraits, start=1):
        contexte += f"[{i}] ({e['source']}, page {e['page']})\n{e['texte']}\n\n"
    return f"""Tu es l'assistant interne d'Altéa Services.
Réponds à la question en utilisant UNIQUEMENT les extraits ci-dessous.
Après chaque information, indique le numéro de l'extrait entre crochets, par exemple [1].
Si les extraits ne contiennent pas la réponse, réponds exactement : "{REPLI}"

Extraits :
{contexte}
Question : {question}
Réponse :"""


def repondre(question, k=3):
    extraits = rechercher(question, k)
    prompt = construire_prompt(question, extraits)
    reponse = client.chat.completions.create(
        model=MODELE,
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )
    return reponse.choices[0].message.content, extraits


if __name__ == "__main__":
    # Q4 : le prompt complet pour une question
    q = "Combien de jours de télétravail par semaine ?"
    print(construire_prompt(q, rechercher(q, 3)))

    # Q5 : 5 questions, dont 2 sans réponse dans la documentation
    questions = [
        "Combien de jours de télétravail par semaine ?",
        "Comment réinitialiser mon mot de passe ?",
        "Comment poser un jour de congé ?",
        "Quel temps fera-t-il demain ?",
        "Quel est le salaire du directeur général ?",
    ]
    for q in questions:
        reponse, extraits = repondre(q)
        print("\n###", q)
        print(reponse)
        print("Sources :", [(e["source"], e["page"]) for e in extraits])

    # Q6 : le LLM seul, sans extraits
    q = "Combien de jours de télétravail par semaine sont autorisés chez Altéa ?"
    direct = client.chat.completions.create(
        model=MODELE, temperature=0,
        messages=[{"role": "user", "content": q}])
    print("\n### SANS RAG :", direct.choices[0].message.content)
    print("### AVEC RAG :", repondre(q)[0])