#!/usr/bin/python3
# coding: utf-8



from indexer import BiInverIndex


if __name__ == "__main__":
    index = BiInverIndex()

    CORPUS_PATH = "./corpus/initiaux"
    
    index.update_index(CORPUS_PATH)

    CORPUS_PATH = "./corpus/complémentaires"
    index.update_index(CORPUS_PATH, update=True)
