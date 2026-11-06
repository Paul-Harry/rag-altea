# test_q11b.py
from etape6_generation import repondre

q = "Qui est couvert par la mutuelle d'entreprise ?"
for k in (3, 5):
    reponse, extraits = repondre(q, k)
    print(f"\n=== k = {k} ===")
    print(reponse)
    print("Sources :", [(e["source"], e["page"]) for e in extraits])