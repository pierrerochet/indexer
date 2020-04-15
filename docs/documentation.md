---
description: |
    API documentation for modules: requester, indexer.

lang: en

classoption: oneside
geometry: margin=1in
papersize: a4

linkcolor: blue
links-as-notes: true
...


    
# Module `requester` {#requester}








    
## Classes


    
### Class `Requester` {#requester.Requester}



> `class Requester(index, sim='euc')`


Le requêteur qui utilise l'index créé par l'indexeur.


#### Attributes

**`index_folder`** :&ensp;`str`
:   Le chemin de l'index.


**`index`** :&ensp;`dict`
:   L'index recupéré du fichier index.json.


**`index_document`** :&ensp;`dict`
:   L'index des documents récupérés du fichier index_document.json.


**`document_size`** :&ensp;`int`
:   Le nombre de document.


**`sim`** :&ensp;`function`
:   La fonction utilisée pour le calcule de similarité.


**`tf`** :&ensp;`function`
:   Fonction pour calcul du tf.


**`idf`** :&ensp;`function`
:   Fonction pour calcul de l'idf.


**`tfidf`** :&ensp;`function`
:   Fonction pour calcul du tfidf.



#### Args

**`index`** :&ensp;`str`
:   Le chemin de l'index sur lequel effectuer les requêtes.


**`sim`** :&ensp;`str`
:   La méthode utilisée pour le calcul de similarité.









    
#### Methods


    
##### Method `filter_documents` {#requester.Requester.filter_documents}



    
> `def filter_documents(self, docs, keywords)`


Les documents sont filtrés en fonction des opérateurs.


###### Args

**`docs`** :&ensp;`dict`
:   le dictionnaire de documents ids - fréquences


**`keywords`** :&ensp;`dict`
:   les mots-clés trés par opérateurs



###### Returns

**`match_docs`** :&ensp;`dict`
:   un nouveau dictionnaire contenant seulements
            les documents respectants les règles des opérateurs



    
##### Method `filter_keywords` {#requester.Requester.filter_keywords}



    
> `def filter_keywords(self, keywords)`


Répartit les mots-clés de la requête en sous-listes en fonction des opérateurs


###### Args

**`keywords`** :&ensp;`list`
:   la liste des mots-clés



###### Returns

**`keywords_clean`** :&ensp;`list`
:   la liste des mots-clés sans les opérateurs


**`keywords_gr`** :&ensp;`dict`
:   un dictionnaire avec les mots-clés triés par opérateur



    
##### Method `get_documents` {#requester.Requester.get_documents}



    
> `def get_documents(self, keywords_gr)`


Extrait les documents qui contiennent les mots-clés de l'index.


###### Args

**`keywords`** :&ensp;`list`
:   le dictionnaire des mots-clés trié par opérateur



###### Returns

**`extrac_docs`** :&ensp;`dict`
:   un dictionnaire contenant 
                les documents extraits,
                les clés sont les ids des documents, 
                les valeurs sont les fréquences associées



    
##### Method `request` {#requester.Requester.request}



    
> `def request(self, keywords)`


Lance la requête.


###### Args

**`keywords`** :&ensp;`list`
:   La liste de mots clés


Trois opérateurs peuvent être utilisés avec les mots-clés :
- + (plus) : le terme doit être présent
- - (moins) : le terme doit être absent
- ø (aucun opérateur) : le terme peut être absent ou présent

###### Returns

**`result`** :&ensp;`list`
:   Le résultat de la requête.



    
##### Method `sorted_documents` {#requester.Requester.sorted_documents}



    
> `def sorted_documents(self, docs, keywords)`


Calcule le score de pertinence des documents, 
puis les ordonne.


###### Args

**`docs`** :&ensp;`dict`
:   le dictionnaire des documents ids - fréquences


**`keywords`** :&ensp;`dict`
:   les mots-clés trés par opérateurs



###### Returns

**`result`** :&ensp;`list`
:   la listes des documents ordonnées en fonction du score de pertinence





    
# Module `indexer` {#indexer}








    
## Classes


    
### Class `BiInverIndex` {#indexer.BiInverIndex}



> `class BiInverIndex(index_path='/INDEX')`


Indexe inversé bilingue français-anglais.


#### Attributes

**`index`** :&ensp;`dict`
:   L'index de la forme 


```python
{'term1':{'id_doc1':freq, 'id_doc2':freq, 'id_doc3':freq, ... }, ... }
```
**`index_document`** :&ensp;`dict`
:   L'index des documents de la forme 


```python
{'id_doc1':{'nom':'nom_doc1', 'titre':'titre_doc1', 'taille':500}, ... }.
```
**`plain_word_fr`** :&ensp;`Pattern`
:   Le regex-pattern pour la détection des lemmes français.


**`plain_word_en`** :&ensp;`Pattern`
:   Le regex-pattern pour la détection des lemmes anglais.



**`fr_tagger`** :&ensp;`TreeTagger`
:   Le tagger pour le français.


**`en_tagger`** :&ensp;`TreeTagger`
:   Le tagger pour l'anglais.



**`save_folder`** :&ensp;`str`
:   Emplacement où l'index est sauvegardé.


**`keep_path`** :&ensp;`str`
:   Le chemin du répertoire où seront stocké les fichiers indexés.


**`index_name`** :&ensp;`str`
:   Le nom du fichier json pour sauvegarder l'index.


**`index_document_name`** :&ensp;`str`
:   Le nom du fichier json pour sauvegarder l'index des documents.



#### Args

**`index_path`** :&ensp;`str`
:   le chemin de l'index.









    
#### Methods


    
##### Method `add_doc` {#indexer.BiInverIndex.add_doc}



    
> `def add_doc(self, file, id)`


Ajoute un document à l'index.


###### Args

**`file`** :&ensp;`str`
:   Le chemin du document à ajouter.


**`id`** :&ensp;`int`
:   l'identifiant du document.



    
##### Method `build_index` {#indexer.BiInverIndex.build_index}



    
> `def build_index(self, corpus_path, update_index=False)`


Construit l'index inversé à partir
d'un réperoire contenant des fichiers xml à indexer.
Les fichiers doivent être sous la forme :
```xml
<article>
    <titre> </titre>
    <texte> </texte>
</article>
```

###### Args

**`corpus_path`** :&ensp;`str`
:   Le chemin du répertoire contenant les fichiers à indexer.


**`update`** :&ensp;`bool`
:   Indique si c'est une mise à jour de l'index. 
            Dans ce cas l'état de l'index actuel sera récupéré. 
            Sinon un nouvel index est crée.  
            Si un index existe déjà il sera supprimé avec accord de l'utilisateur
            False par défaut.  



###### Returns

**`index`** :&ensp;`dict`
:   L'index nouvellement crée.



    
##### Method `check_state` {#indexer.BiInverIndex.check_state}



    
> `def check_state(self)`


Vérifie si un dossier "INDEX" existe déjà et s'il contient bien les élements requis.

Returns: 
    True si l'index est en bon état, False si l'index n'a pas été trouvé ou s'il est détérioré.


    
##### Method `clean_state` {#indexer.BiInverIndex.clean_state}



    
> `def clean_state(self)`


Tente de nettoyer l'environnement d'index. 
Vérifie si le dossier "INDEX" existe déjà.
Une demande de confirmation est demandée avant de les supprimer.


###### Returns

True si il n'y avait pas d'état ou que l'état a bien été réinitialisé. False si l'utilisateur a refusé le nettoyage.


    
##### Method `dump` {#indexer.BiInverIndex.dump}



    
> `def dump(self)`


Sauvegarde l'index et l'index de document dans des fichiers json 
nommés "index.json" et "index_document.json".


    
##### Method `get_stats` {#indexer.BiInverIndex.get_stats}



    
> `def get_stats(self, text)`


Récupère la fréquence des termes contenus dans un texte.


###### Args

**`text`** :&ensp;`str`
:   Le textes à utiliser.


Returns :
    freq_term (dict): Les fréquences des termes trouvés dans le texte.
    size (int): Le nombre total de token dans le texte.


    
##### Method `import_index` {#indexer.BiInverIndex.import_index}



    
> `def import_index(self)`


Récupère l'état actuel de l'index.
Utilisé dans le cas d'un mise à jour de l'index.


###### Returns

**`currents_docs`** :&ensp;`list`
:   La liste des documents actuellement indexés.


**`id`** :&ensp;`int`
:   Le nouvel id, où va commencer l'indexation.



    
##### Method `keep_doc` {#indexer.BiInverIndex.keep_doc}



    
> `def keep_doc(self, file)`


Copie un document dans le dossier de sauvegarde :
documentsIndex.


###### Args

**`file`** :&ensp;`str`
:   Le chemin du fichier à copier.



    
##### Method `parse_doc` {#indexer.BiInverIndex.parse_doc}



    
> `def parse_doc(self, xml_file)`


Parse un document xml de la forme :
```xml
<article>
    <titre> </titre>
    <texte> </texte>
</article>
```


###### Args

**`xml_file`** :&ensp;`str`
:   Le chemin du fichier xml.



###### Returns

**`text`** :&ensp;`str`
:   Le contenu de la balise texte du fichier.


**`title`** :&ensp;`str`
:   Le contenu de la balise title du fichier.




-----
Generated by *pdoc* 0.7.5 (<https://pdoc3.github.io>).
