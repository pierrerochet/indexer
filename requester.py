import argparse
import json
import math

import numpy as np
from numpy import dot
from numpy.linalg import norm

from scipy.spatial.distance import cosine, euclidean


class Requester:
    """Le requêteur qui utilise l'index créé par l'indexeur.
    
    Args: 
        index (str): le chemin de l'index sur lequel effectuer les requêtes

    Attributes:
        index_folder (str): le chemin de l'index
        index (dict): l'index recupéré du fichier index.json 
        index_document (dict): l'index des documents récupéré du fichier index_document.json
        document_size (int): le nombre de document
        score_func (function): la fonction utilisée pour le calcule de similarité
        pond (function): la fonction utilisée pour la pondération
    """

    def __init__(self, index):
        self.index_folder = index

        index_name = index + "/index.json"
        self.index = json.load(open(index_name, "r", encoding="utf8"))
        index_document_name = index + "/index_document.json"
        self.index_document = json.load(open(index_document_name, "r", encoding="utf8"))

        self.document_size = len(self.index_document)


        # Pour la calcul de similarité
        # self.sim = lambda v1, v2 : dot(v1, v2)/(norm(v1)*norm(v2))
        # self.sim = cosine
        self.sim = euclidean
        
        ## Test de plusieurs fonctions de pondération :
        # fonction sigmoid
        # self.pond = lambda x: 1 / (1 + np.exp(-x))
        # fonction de gauss
        # self.pond = lambda x: [((1.0 + math.erf(v / math.sqrt(2.0))) / 2.0) for v in x] 
        
        # Pour le calcul du tf-idf
        self.tf = lambda x, size : np.array([v if v > 0 else 0 for v in x ]) / size
        self.idf = lambda x : np.array([(np.log2(self.document_size/v)) if v > 0 else 0 for v in x ])
        self.tfidf = lambda x, size : self.tf(x, size) * self.idf(x)



    def request(self, keywords:list) -> list:
        """
        Lance la requête.

        Args:
            keywords (list): la liste de mots clés
            Trois opérateurs peuvent être utilisés avec les mots-clés :
            + (plus) : le terme doit être présent
            - (moins) : le terme doit être absent
            ø (aucun opérateur) : le terme peut être absent ou présent
        
        Return:
            result (list): les résultats de la reqûete
        """
        # -- Etape 1 : On trie les mots-clés
        keywords, keywords_gr = self.filter_keywords(keywords)

        # -- Etape 2 : On récupère les documents contenant les mots-clés
        docs = self.get_documents(keywords)

        # -- Etape 3 : Les documents sont filtrés en fonction des mots-clés
        docs = self.filter_documents(docs, keywords_gr)

        # -- Etape 4 : Les documents sont triés par score de pertience
        result = self.sorted_documents(docs, keywords_gr)
        return result


    def filter_keywords(self, keywords:list) -> (list, dict):
        """
        Répartit les mots-clés de la requête en sous-listes en fonction des opérateurs

        Args:
            keywords (list): la liste des mots-clés

        Returns:
            keywords_clean (list): la liste des mots-clés sans les opérateurs
            keywords_gr (dict): un dictionnaire avec les mots-clés triés par opérateur
        """
        keywords_gr = {"P":[], "A":[], "O":[]}
        for word in keywords:
            if word.startswith("+"): keywords_gr["P"].append(word[1:])
            elif word.startswith("-"): keywords_gr["A"].append(word[1:])
            else: keywords_gr["O"].append(word)
        
        keywords_clean = [kw for lkw in keywords_gr.values() for kw in lkw]
        return keywords_clean, keywords_gr



    def get_documents(self, keywords:list) -> dict:
        """
        Extrait les documents qui contiennent les mots-clés de l'index.

        Args:
            keywords (list): la liste des mots clées

        Returns:
            extrac_docs (dict): un dictionnaire contenant 
                            les documents extraits,
                            les clés sont les ids des documents, 
                            les valeurs sont les fréquences associées
        """
        extract_docs = {}
        for word in keywords:
            for doc_id, freq in self.index[word].items():
                doc = extract_docs.setdefault(doc_id, {})
                doc.update({word:freq})

        return extract_docs


    def filter_documents(self, docs:dict, keywords:dict) -> dict:
        """
        Les documents sont filtrés en fonction des opérateurs.

        Args:
            docs (dict): le dictionnaire de documents ids - fréquences
            keywords (dict): les mots-clés trés par opérateurs

        Returns:
            match_docs (dict): un nouveau dictionnaire contenant seulements
                        les documents respectants les règles des opérateurs 

        """

        def check_doc(doc) -> dict:
            terms = doc[1]
            if all(word in terms for word in keywords["P"]) == False:
                return False
            if any(word in terms for word in keywords["A"]):
                return False
            return True

        match_docs = dict(filter(check_doc, docs.items()))
        return match_docs


    def sorted_documents(self, docs:dict, keywords:dict) -> list:
        """
        Calcule le score de pertinence des documents, 
        puis les ordonne.

        Args:
            docs (dict): le dictionnaire des documents ids - fréquences
            keywords (dict): les mots-clés trés par opérateurs

        Returns:
            result (list) : la listes des documents ordonnées en fonction du score de pertinence
        """

        keywordsPO = keywords["P"] + keywords["O"]
        docs_similarity = {}

        # s'il y un qu'un mot-clé on se base sur les fréquences relative
        if len(keywordsPO) == 1:
            for id, freqs in docs.items():
                size = self.index_document[id]["taille"]
                freq = freqs[keywordsPO[0]] / size
                docs_similarity[id] = freq
        
        # sinon on effectue un tf-idf + calcul de similarité
        else:
            for id, freqs in docs.items():
            
                # la taille du document
                size = self.index_document[id]["taille"]

                # le vecteur de la requête
                vec_ref = np.ones(len(keywordsPO))

                # le vecteur tf-idf de la référence
                tfidf_ref = self.tfidf(vec_ref, size)

                # le vecteur du document
                vecteur_doc = np.array([freqs.get(word, 0) for word in keywordsPO])
                # le vecteur tf-idf du document
                tfidf_doc = self.tfidf(vecteur_doc, size)

                # calcule du score de similarité entre les deux vecteurs
                score = self.sim(tfidf_doc, tfidf_ref)

                # sauvegarde de la valeur 
                docs_similarity[id] = score


        # on ordonne les documents en fonction des scores précédemments calculés
        result_sorted = sorted(docs_similarity.items(), key=lambda x: x[1], reverse=True )


        # on ajoute des informations supplémentaires à nos résultats
        result = []
        for doc in result_sorted:
            id_doc, score = doc
            title, _, size = self.index_document[id_doc].values()
            result.append((score, title, docs[id_doc], size))
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
        score, title, terms, size = doc
        print(f"{rank}.", score, title, terms, size, sep="\t")
