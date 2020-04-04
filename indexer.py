import glob
import json
import os
import re
import shutil
import xml.etree.ElementTree as ET

import treetaggerwrapper
from langdetect import detect


class BiInverIndex:

    def __init__(self):
        self.index = {}
        self.plain_word_fr = re.compile("ABR|ADJ|NAM|NOM|VER")
        self.plain_word_en = re.compile("JJ|NP|NN|VB")
        self.keep_path = "documentsIndex"
        self.index_name = "index.json"

    def dump(self, path):
        with open(path, "w", encoding="utf8") as doc:
            json.dump(self.index, doc, indent=4)

    def keep_doc(self, file):
        if not os.path.isdir(self.keep_path):
            os.mkdir(self.keep_path)
        shutil.copy(file, self.keep_path)


    def __check_state(self):
        if os.path.isfile(self.index_name) and os.path.isdir(self.keep_path):
            json_index = open(self.index_name, "r", encoding="utf8")
            current_index = json.load(json_index)
            json_index.close()
            self.index = current_index
            current_docs = os.listdir(self.keep_path)
            id = len(current_docs)
        else:
            current_docs = []
            id = 0
        return current_docs, id

    def __clean_state(self):
        if os.path.exists(self.keep_path) :
            if os.path.isdir(self.keep_path):
                resp = None
                while resp != "n" and resp != "y":
                    resp = input( "Warning ! Le dossier 'documentsIndex' existe déjà, son contenu sera supprimé. Continuer ? (Y/N) " )
                    resp = resp.lower()
                if resp == "n" : return False
                for file in glob.glob(self.keep_path + "/*"):
                    os.remove(file)
        
        if os.path.exists(self.index_name) :
            if os.path.isfile(self.index_name):
                resp = None
                while resp != "n" and resp != "y":
                    resp = input( "Warning ! Le fichier 'index.json' existe déjà, son contenu sera supprimé. Continuer ? (Y/N) " )
                    resp = resp.lower()
                if resp == "n" : return False
                os.remove(self.index_name)

        return True

    def __parse_doc(self, file):
        doc = ET.parse(file)
        root = doc.getroot()
        text = root.find("texte").text
        title = root.find("titre").text
        return text, title

    def __add_doc(self, file, id = 0):
        freq_term = {}

        text, _ = self.__parse_doc(file)
        lang = detect(text)

        tagger = treetaggerwrapper.TreeTagger(TAGLANG=detect(text))
        tagged_text = tagger.tag_text(text)

        for token in tagged_text:
            elements = token.split("\t")
            if len(elements) == 3:
                _, pos, lemma = elements
                if re.match(self.__getattribute__("plain_word_" + lang), pos) != None:
                    freq_term[lemma] = freq_term.get(lemma,0) + 1

        for term, freq in freq_term.items():
            r = self.index.get(term, {})
            r.update({id:freq})
            self.index[term] = r
        
        self.keep_doc(file)


    def update_index(self, corpus_path, update = False):
        
        if update == True :
            current_docs, id = self.__check_state()
            print("\n--- Mise à jour de l'index")

        else :
            if self.__clean_state() == False : return
            print("\n--- Construction de l'index")
            current_docs, id = [], 0

        files = glob.glob(corpus_path + "/*")
        for file in files:
            file_name = file.split("/")[-1]
            print("fichier :: " + file_name)

            if file_name in current_docs:
                print("ERROR :: Le document est déjà indexé, il sera ignoré")
            else:
                self.__add_doc(file, id)
                current_docs.append(file)
                id += 1

        self.dump(self.index_name)
        print("Terminé.")