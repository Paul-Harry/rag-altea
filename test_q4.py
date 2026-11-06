# test_q4.py
from etape1_collecte import collecter
from etape2_nettoyage import nettoyer

p = next(x for x in collecter()
         if x["source"] == "mutuelle.pdf" and x["page"] == 2)
print("AVANT :", repr(p["texte"][:300]))
print("\nAPRÈS :", repr(nettoyer(p["texte"])[:300]))