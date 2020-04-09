import argparse
import json
import math

import numpy as np
from numpy import dot
from numpy.linalg import norm


class Requester:

    def __init__(self, index):
        self.index_folder = index

        self.index_name = index + "/index.json"
        self.index = json.load(open(self.index_name, "r", encoding="utf8"))

        self.index_document_name = index + "/index_document.json"
        self.index_document = json.load(open(self.index_document_name, "r", encoding="utf8"))

        # similarité cosinus
        self.score_func = lambda v1, v2 : dot(v1, v2)/(norm(v1)*norm(v2))
        
        ## Test de plusieurs fonctions de pondération :
        # fonction sigmoid
        # self.pond = lambda x: 1 / (1 + np.exp(-x))
        # fonction de gauss
        # self.pond = lambda x: [((1.0 + math.erf(v / math.sqrt(2.0))) / 2.0) for v in x] 
        # fonction percent (meilleure pondération il semblerait)
        self.pond = lambda x: x / sum(x)


    def request(self, keywords:list) -> list:
        """
        Affiche les quatre étapes du pipeline
        """
        
        print("-- Etape 1 : On trie les mots-clés")
        keywords = self.filter_keywords(keywords)
        print("Mots à inclure : ", self.keywordsP)
        print("Mots à exclure : ", self.keywordsM)
        print("Mots optionnels : ", self.keywordsO)
        print()
        
        print("-- Etape 2 : On récupère les documents contenant les mots-clés")
        docs = self.get_documents(keywords)
        print(*docs.items(), sep="\n")
        print()

        print("-- Etape 3 : Les documents sont filtrés en fonction des mots-clés")
        docs = self.filter_documents(docs)
        print(*docs.items(), sep="\n")
        print()

        print("-- Etape 4 : Les documents sont triés par score de pertience")
        result = self.sorted_documents(docs)
        return result


    def filter_keywords(self, keywords:list) -> (list, list, list):
        """
        Filtre les mots clés en fonction de trois différents opérateurs
            + (plus) : le terme doit être présent
            - (moins) : le terme doit être absent
            ø (aucun opérateur) : le terme peut être absent ou présent
        """
        
        keywordsP = []
        keywordsM = []
        keywordsO = []
        for word in keywords:
            if word.startswith("+"): keywordsP.append(word[1:])
            elif word.startswith("-"): keywordsM.append(word[1:])
            else: keywordsO.append(word)

        self.keywordsP = keywordsP
        self.keywordsM = keywordsM
        self.keywordsO = keywordsO
        keywords = keywordsP + keywordsM + keywordsO
        return keywords



    def get_documents(self, keywords:list) -> dict:
        """
        Match les documents avec leurs IDs
        """
        
        match_docs = {}
        for word in keywords:
            for doc_id, freq in self.index[word].items():
                doc = match_docs.setdefault(doc_id, {})
                doc.update({word:freq})

        return match_docs


    def filter_documents(self, docs:dict) -> dict:
        """
        Filtre les documents selon la présence de trois genres de mots
        
        Returns:
            False si tous les mots ne sont pas présents dans la liste keywordsP
                  ou s'il existe un mot qui est présent dans la liste keywordsM
                  
            True
        """
        
        def check_doc(doc):
            terms = doc[1]
            if all(word in terms for word in self.keywordsP) == False:
                return False
            if any(word in terms for word in self.keywordsM):
                return False
            return True

        match = dict(filter(check_doc, docs.items()))
        return match


    def sorted_documents(self, docs:dict) -> list:
        """
        Trie les documents selon leur pertinence calculée par la similarité cosinus
        """

        keywordsPO = self.keywordsP + self.keywordsM
        vec_ref = np.ones(len(keywordsPO))
        docs_similarity = {}

        for id, freqs in docs.items():
            v = np.array([freqs.get(word, 0) for word in keywordsPO])
            vecteur = self.pond( v )
            docs_similarity[id] = self.score_func( vecteur, vec_ref )

        result_sorted = sorted(docs_similarity.items(), key=lambda x: x[1], reverse=True)

        result = []
        for doc in result_sorted:
            id_doc, score = doc
            result.append((score, self.index_document[id_doc]["title"], docs[id_doc]))

        return result


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
   
    parser.add_argument("keywords", type=str, help="les mots-clés de la requête")
    parser.add_argument("-i", "--index", type=str, default="./INDEX", help="emplacement de l'index")
   
    args = parser.parse_args()
    index = args.index
    keywords = args.keywords.split(" ")

    requester = Requester(index)
    result = requester.request(keywords)

    print(f"%%% {len(result)} document(s) trouvé(s)")
    for rank, doc in enumerate(result, 1):
        score, title, terms = doc
        print(f"{rank}.", score, title, terms, sep="\t")
