import argparse
import json
import math

import numpy as np
from numpy import dot
from numpy.linalg import norm

from scipy.spatial.distance import cosine, euclidean


class Requester:
    """Le requêteur qui utilise l'index créé par l'indexeur.

    Attributes:
        index_folder (str): Le chemin de l'index.
        index (dict): L'index recupéré du fichier index.json.
        index_document (dict): L'index des documents récupérés du fichier index_document.json.
        document_size (int): Le nombre de document.
        sim (function): La fonction utilisée pour le calcule de similarité.
        tf (function): Fonction pour calcul du tf.
        idf (function): Fonction pour calcul de l'idf.
        tfidf (function): Fonction pour calcul du tfidf.

    Args:
        index (str): Le chemin de l'index sur lequel effectuer les requêtes.
        sim (str): La méthode utilisée pour le calcul de similarité.

    """

    def __init__(self, index:str, sim:str="euc"):
        # chemin de l'index
        self.index_folder = index

        # index des termes
        index_name = index + "/index.json"
        self.index = json.load(open(index_name, "r", encoding="utf8"))
        
        # index des documents
        index_document_name = index + "/index_document.json"
        self.index_document = json.load(open(index_document_name, "r", encoding="utf8"))

        # nombre total de document ( = taille de l'index des documents )
        self.document_size = len(self.index_document)

        # Pour la calcul de similarité
        # self.sim = lambda v1, v2 : dot(v1, v2)/(norm(v1)*norm(v2))
        if sim == "cos": self.sim = cosine
        if sim == "euc": self.sim = euclidean

        # Pour le calcul du tf-idf
        # | ----

        # formule du tf :
        # - si fréquence > 0 : fréquence / nb de mot * 100 ( x 100 pour un effectuer un changement d'echelle )
        # - si fréquence = 0 : 0
        self.tf = lambda x, size : np.array([v if v > 0 else 0 for v in x ]) / size * 100
        
        def idf(kw_PO):
            result = np.zeros(len(kw_PO))
            for i, kw in enumerate(kw_PO):
                # formule de l'idf : log2( nb de doc / nb de doc contenant le mot )
                n_doc = len(self.index[kw])
                result[i] = np.log2(self.document_size/n_doc)
            return result
        self.idf = idf

        self.tfidf = lambda x, size, kw_PO : self.tf(x, size) * self.idf(kw_PO)
        # ---- |

        ## Test de plusieurs fonctions de pondération ( non concluant ):
        # fonction sigmoid
        # self.pond = lambda x: 1 / (1 + np.exp(-x))
        # fonction de gauss
        # self.pond = lambda x: [((1.0 + math.erf(v / math.sqrt(2.0))) / 2.0) for v in x] 
        
        
    def request(self, keywords:list) -> list:
        """
        Lance la requête.

        Args:
            keywords (list): La liste de mots clés
            Trois opérateurs peuvent être utilisés avec les mots-clés :
            - + (plus) : le terme doit être présent
            - - (moins) : le terme doit être absent
            - ø (aucun opérateur) : le terme peut être absent ou présent
        
        Returns:
            result (list): Le résultat de la requête.
        """
        # -- Etape 1 : On trie les mots-clés
        keywords, keywords_gr = self.filter_keywords(keywords)

        # -- Etape 2 : On récupère les documents contenant les mots-clés
        docs = self.get_documents(keywords_gr)

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



    def get_documents(self, keywords_gr:dict) -> dict:
        """
        Extrait les documents qui contiennent les mots-clés de l'index.

        Args:
            keywords (list): le dictionnaire des mots-clés trié par opérateur

        Returns:
            extrac_docs (dict): un dictionnaire contenant 
                            les documents extraits,
                            les clés sont les ids des documents, 
                            les valeurs sont les fréquences associées
        """
        extract_docs = {}
        for word in keywords_gr["P"] + keywords_gr["O"]:
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
            result (list): la listes des documents ordonnées en fonction du score de pertinence
        """

        keywordsPO = keywords["P"] + keywords["O"]
        docs_similarity = {}

        # s'il y a qu'un mot-clé on se base sur les fréquences relatives du mot
        if len(keywordsPO) == 1:
            for id, freqs in docs.items():

                # la taille du document
                size = self.index_document[id]["taille"]

                # la fréquence relative
                freq = freqs[keywordsPO[0]] / size

                # on sauvegarde le score
                docs_similarity[id] = freq
        
        # sinon on effectue un tf-idf + calcul de similarité
        else:
            for id, freqs in docs.items():
            
                # la taille du document
                size = self.index_document[id]["taille"]

                # le vecteur de la requête
                vec_ref = np.ones(len(keywordsPO))
                # le vecteur tf-idf de la référence
                tfidf_ref = self.tfidf(vec_ref, size, keywordsPO)

                # le vecteur du document
                vecteur_doc = np.array([freqs.get(word, 0) for word in keywordsPO])
                
                # le vecteur tf-idf du document
                tfidf_doc = self.tfidf(vecteur_doc, size, keywordsPO)
                # print(vecteur_doc, tfidf_doc)
                # calcule du score de similarité entre les deux vecteurs
                score = self.sim(tfidf_doc, tfidf_ref)

                # sauvegarde de la valeur 
                docs_similarity[id] = score


        # on ordonne les documents en fonction des scores précédemments calculés
        # -- on oriente le sens de l'odre suivant la fonction de similarité 
        if self.sim.__name__ == "cosine" and len(keywordsPO) != 1 : reverse = False
        else : reverse = True
        result_sorted = sorted(docs_similarity.items(), key=lambda x: x[1], reverse=reverse )

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
    parser.add_argument("-s", "--similarity", type=str, default="enc", help="type de similarité à utiliser: 'enc' pour euclidienne, 'cos' pour cosinus. euclienne par défaut")

    args = parser.parse_args()
    index = args.index
    keywords = args.keywords.split(" ")
    sim = args.similarity

    requester = Requester(index, sim=sim)
    result = requester.request(keywords)

    print(f"%%% {len(result)} document(s) trouvé(s)")
    for rank, doc in enumerate(result, 1):
        score, title, terms, size = doc
        print(f"{rank}.", score, title, terms, size, sep="\t")
