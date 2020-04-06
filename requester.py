import json

index_file = "INDEX/index.json"
with open(index_file, "r", encoding="utf8") as file:
    index = json.load(file)


### 1. On trie les mots-clés
keywords = ["+avoir","+etre","accord","-gouvernement" ]
keywordsP = []
keywordsM = []
keywordsO = []
for word in keywords:
    if word.startswith("+"): keywordsP.append(word[1:])
    elif word.startswith("-"): keywordsM.append(word[1:])
    else: keywordsO.append(word)

print("-- Etape 1 : On trie les mots-clés")
print("Mots à inclure : ", keywordsP)
print("Mots à exclure : ", keywordsM)
print("Mots optionnels : ", keywordsO)
print()

### 2. On récupère les documents contenant tous les mots-clés
match_docs = {}
for word in keywordsP + keywordsM + keywordsO:
    for doc_id, freq in index[word].items():
        doc = match_docs.setdefault(doc_id, {})
        doc.update({word:freq})

print("-- Etape 2 : On récupère les documents contenant les mots-clés")
print(*match_docs.items(), sep="\n")
print()


### 3. On filtre les document en fonction des mots-clés demandés
def check_doc(doc):
    terms = doc[1]
    if all(word in terms for word in keywordsP) == False:
        return False
    if any(word in terms for word in keywordsM):
        return False
    return True

print("-- Etape 3 : Les documents sont filtrés en fonction des mots-clés")
match = list(filter(check_doc, match_docs.items()))
print(*match, sep="\n")
print()


### 4. Calcule du score de pertinence
import numpy as np
from numpy import dot
from numpy.linalg import norm
import math

## Test de plusieurs fonctions de pondération :
# fonction sigmoid
sigmoid = lambda x: 1 / (1 + np.exp(-x))
# fonction de gauss
gauss = lambda x: [((1.0 + math.erf(v / math.sqrt(2.0))) / 2.0) for v in x] 
# fonction percent (meilleure pondération il semblerait)
percent = lambda x: x / sum(x)

# similarité cosinus
score = lambda v1, v2 : dot(v1, v2)/(norm(v1)*norm(v2))

# le vecteur de référence pour calculer la similarité
keywordsPO = keywordsP + keywordsO
vec_ref = np.ones(len(keywordsPO))

docs_similarity = {}
for id, freqs in match:
    v = np.array([freqs.get(word, 0) for word in keywordsPO])
    # vecteur = sigmoid( v )
    # vecteur = gauss( v )
    vecteur = percent( v )
    docs_similarity[id] = score( vecteur, vec_ref )


### Résulat
print("-- Etape 4 : Les documents sont triés par score de pertience")
result_sorted = sorted(docs_similarity.items(), key=lambda x: x[1], reverse=True)

index_doc_file = "INDEX/index_document.json"
with open(index_doc_file, "r", encoding="utf8") as file:
    index_doc = json.load(file)

match = dict(match) # temporaine, pour faciliter l'affichage
print(f"%%% {len(result_sorted)} document(s) trouvé(s)")
for rank, doc in enumerate(result_sorted, 1):
    id_doc, score = doc
    print(f"{rank}.", score, index_doc[id_doc]["title"], match[id_doc], sep="\t")





