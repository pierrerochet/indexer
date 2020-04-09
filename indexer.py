#!/usr/bin/python3
# coding: utf-8

import argparse
import glob
import json
import os
import re
import shutil
import sys
import xml.etree.ElementTree as ET

import treetaggerwrapper
from langdetect import detect
from termcolor import colored

from unidecode import unidecode


class BiInverIndex:
    """Indexe inversé bilingue français-anglais.

    Attributes:
        index (dict): L'index de la forme {'term':{'id_doc1':freq, 'id_doc2':freq, 'id_doc3':freq, ... }.
        plain_word_fr (Pattern): Le regex-pattern pour la détection des lemmes français.
        plain_word_en (Pattern): Le regex-pattern pour la détection des lemmes anglais.
        fr_tagger (TreeTagger): Le tagger pour le français.
        en_tagger (TreeTagger): Le tagger pour l'anglais.
        keep_path (str): Le nom du répertoire où seront stocké les fichiers indexés.
        index_name (str): le nom du fichier json pour sauvegarder l'index.
    """

    def __init__(self, index_path="/INDEX"):
        self.index = {}
        self.index_document = {}
        self.plain_word_fr = re.compile("ABR|ADJ|NAM|NOM|VER")
        self.plain_word_en = re.compile("JJ|NP|NN|VB")
        self.fr_tagger = treetaggerwrapper.TreeTagger(TAGLANG="fr")
        self.en_tagger = treetaggerwrapper.TreeTagger(TAGLANG="en")
        self.save_folder = index_path
        self.keep_path = self.save_folder + "/documentsIndex"
        self.index_name = self.save_folder + "/index.json"
        self.index_document_name = self.save_folder + "/index_document.json"


    def keep_doc(self, file:str):
        """
        Copie un document dans le dossier de sauvegarde :
        documentsIndex.

        Args:
            file (str): Le chemin du fichier à copier.

        """
        shutil.copy(file, self.keep_path)


    def check_state(self):
        """
        Vérifie si un dossier "INDEX" existe déjà et s'il contient bien les élements requis.

        Returns: 
            True si l'index est en bon état, False si l'index n'a pas été trouvé ou s'il est détérioré.
        """

        # Vérifie qu'un dossier "INDEX" existe
        if os.path.isdir(self.save_folder) == False:
            print( colored("Error", "red"), "Aucun index n'a été trouvé. ", sep=" : ")
            return False

        # Vérifie que les fichiers "index.json", "index_docoment.json" et que le dossier "documentsIndex" existent
        state_index_name = os.path.isfile(self.index_name)
        state_index_document = os.path.isfile(self.index_document_name)
        state_keep_path = os.path.isdir(self.keep_path)

        if not state_index_document == state_index_name == state_keep_path == True:
            print( colored("Error", "red"), "Un index a bien été trouvé mais il semble détérioré. ", sep=" : ")
            return False


        return True


    def clean_state(self) -> bool:
        """
        Tente de nettoyer l'environnement d'index. 
        Vérifie si le dossier "INDEX" existe déjà.
        Une demande de confirmation est demandée avant de les supprimer.

        Returns:
            True si il n'y avait pas d'état ou que l'état a bien été réinitialisé. False si l'utilisateur a refusé le nettoyage.

        """
        # Si "INDEX" existe, on demande la confirmation de le réinitioaliser
    
        if os.path.exists(self.save_folder) :
            if os.path.isdir(self.save_folder):
                resp = None
                while resp != "n" and resp != "y":
                    resp = input( colored("Warning", "yellow") + f" : Le dossier {self.save_folder} existe déjà, son contenu sera supprimé. Continuer ? (Y/N) " )
                    resp = resp.lower()
                if resp == "n" : return False
                shutil.rmtree(self.save_folder)
    
        os.mkdir(self.save_folder)
        os.mkdir(self.keep_path)
        return True


    def parse_doc(self, xml_file:str) -> (str, str):
        """
        Parse un document xml de la forme :
        ```xml
        <article>
            <titre> </titre>
            <texte> </texte>
        </article>
        ```

        Args:
            xml_file (str): Le chemin du fichier xml.

        Returns:
            text (str): Le contenu de la balise texte du fichier.
            title (str): Le contenu de la balise title du fichier.
        """
        doc = ET.parse(xml_file)
        root = doc.getroot()
        text = root.find("texte").text
        title = root.find("titre").text
        return text, title


    def get_stats(self, text:str) -> (dict, int):
        """
        Récupère la fréquence des termes contenus dans un texte.

        Args (str):
            Le textes à utiliser.
        
        Returns (dict):
            Les fréquences des termes trouvés dans le texte.
        """
        freq_term = {}
        # Détection de la langue
        lang = detect(text)
        # Tagging du texte
        tagged_text = self.__getattribute__(lang + "_tagger").tag_text(text)
        # On récupère seleument les fréquences des tokens ayant un lemma 
        # qui match avec le pattern de la langue détectée
        size = 0
        for token in tagged_text:
            size += 1
            elements = token.split("\t")
            if len(elements) == 3:
                _, pos, lemma = elements
                if re.match(self.__getattribute__("plain_word_" + lang), pos) != None:
                    lemma = lemma.lower()
                    lemma = unidecode(lemma)
                    freq_term[lemma] = freq_term.get(lemma,0) + 1
        return freq_term, size


    def add_doc(self, file:str , id:int):
        """
        Ajoute un document à l'index.

        Args:
            file (str): Le chemin du document à ajouter.
            id: (int): l'identifiant du document.
        """
        # On récupère le contenu du document
        text, title = self.parse_doc(file)
        # On récupère la fréquence des termes qu'il contient
        freq_term, size = self.get_stats(text)
        # On met à jour l'index
        for term, freq in freq_term.items():
            r = self.index.setdefault(term, {})
            r.update({id:freq})
        # On sauvegarde le document
        title = title.split("\n", 1)[0]
        name = file.split("/")[-1]
        self.index_document[id] = {"nom":name, "title":title, "taille":size}
        self.keep_doc(file)


    def import_index(self) -> (list, int):
        """
        Récupère l'état actuel de l'index.
        Utilisé dans le cas d'un mise à jour de l'index.

        Returns:
            currents_docs (list): La liste des documents actuellement indexés.
            id (int): Le nouvel id, où va commencer l'indexation.
        """

        json_index = open(self.index_name, "r", encoding="utf8")
        current_index = json.load(json_index)
        json_index.close()
        self.index = current_index

        json_index_document = open(self.index_document_name, "r", encoding="utf8")
        current_index_document = json.load(json_index_document)
        json_index_document.close()
        self.index_document = current_index_document

        current_docs = os.listdir(self.keep_path)
        id = len(self.index_document)

        return current_docs, id


    def build_index(self, corpus_path:str, update_index=False) -> dict:
        """
        Construit l'index inversé à partir
        d'un réperoire contenant des fichiers xml à indexer.
        Les fichiers doivent être sous la forme :
        ```xml
        <article>
            <titre> </titre>
            <texte> </texte>
        </article>
        ```
        Args:
            corpus_path (str): Le chemin du répertoire contenant les fichiers à indexer.
            update (bool): Indique si c'est une mise à jour de l'index. 
                        Dans ce cas l'état de l'index actuel sera récupéré. 
                        Sinon un nouvel index est crée.  
                        Si un index existe déjà il sera supprimé avec accord de l'utilisateur
                        False par défaut.  
        
        Returns:
            L'index
        """ 

        # Si c'est une mise à jour de l'index on récupère l'état actuel de l'index
        # Si l'index existant est détérioré le programme s'arrête
        if update_index == True :
            if self.check_state() == False: return
            current_docs, id = self.import_index()
            print("\n--- Mise à jour de l'index")

        # Sinon on vérifie qu'il n'y ait pas de fichier qui entre en conflit
        # Si un index est détecté on le supprime
        # Si ce n'est pas possible alors on arrête le programme
        # Si le nettoyage est confirmé alors on initialise
        # notre liste de documents déjà traités et l'id 
        else :
            if self.clean_state() == False : return
            print("\n--- Construction de l'index")
            current_docs, id = [], 0

        # On récupère le chemin des fichiers à indexer
        files = glob.glob(corpus_path + "/*")

        
        for file in files:

            # On affiche le nom du fichier en cours de traitement 
            file_name = file.split("/")[-1]
            print("fichier", file_name, sep=" :: ", end=" -> ")

            # Si le document a déjà été indexé, on l'ignore
            if file_name in current_docs:
                print( colored("Warning", "yellow"), "Document déjà indexé, il sera ignoré", sep=" : ")
            
            # Si le document n'a pas déjà été indexé
            # - on l'ajoute à l'index, 
            # - on le place dans notre liste des documents traités
            # - on incrémente l'id
            else:
                self.add_doc(file, id)
                current_docs.append(file)
                id += 1
                print(colored("OK", "green"))

        # Quand tous les documents du dossier ont été traités
        # on sauvegarde notre index
        self.dump()
        print("Terminé.")

        return self.index


    def dump(self):
        """
        Sauvegarde l'index et l'index de document dans des fichiers json 
        nommés "index.json" et "index_document.json".

        """
        with open(self.index_name, "w", encoding="utf8") as index_file:
            json.dump(self.index, index_file, indent=4)
        
        with open(self.index_document_name, "w", encoding="utf8") as index_doc_file:
            json.dump(self.index_document, index_doc_file, indent=4)



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", type=str, help="le chemin du dossier contenant le corpus à indexer")

    parser.add_argument("-i", "--index", type=str, default="./INDEX", help="le nom de l'index")
    parser.add_argument("-u", "--update", action="store_true", help="indique s'il faut effectuer une mise à jour de l'index. l'option --index pointra alors vers un index existant")
    
    args = parser.parse_args()

    index = BiInverIndex(args.index)

    index.build_index(args.corpus, args.update)
