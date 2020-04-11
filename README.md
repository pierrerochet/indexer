# Indexer

`pip install -r requirements.txt`

## Usage
`
python3 indexer.py [-h] [-i INDEX] [-u] corpus
`

## Exemple
`
python3 indexer.py corpus/initiaux/
`

```console
--- Construction de l'index
fichier :: 2002-02-BEILIN-16167.txt -> OK
fichier :: 2001-08-FRANK-15516.txt -> OK
fichier :: 2002-07-TSHIYEMBE-16697.txt -> OK
fichier :: 2002-07-MOTCHANE-16708.txt -> OK
fichier :: 103433-article.txt -> OK
fichier :: 2003-01-KAPELIOUK-9652.txt -> OK
fichier :: 103310-article.txt -> OK
fichier :: 2001-01-DRWESKI-14685.txt -> OK
```
`
python3 indexer.py -u corpus/complémentaires/
`
```console
--- Mise à jour de l'index
fichier :: 103687-article.txt -> OK
fichier :: 2003-04-LAURENS-10112.txt -> OK
```

## Argument obligatoire

argument | description
:-|:-
corpus | le chemin du dossier contenant le corpus à indexer


## Arguments optionnels

argument | description
:-|:-
-i, --index INDEX | emplacement de l'index, cherche à l'emplacement actuel par défaut
-u, --update | indique s'il faut effectuer une mise à jour de l'index. l'option --index pointra alors vers un index existant
-h, --help | affiche l'aide

# Requester

## Usage
`
python3 requester.py [-h] [-i INDEX] [-s {cos,euc}] keywords
`


3 opérateurs possibles sur les termes :
- \+ (plus) : le terme doit être présent
- \- (moins) : le terme doit être absent
- ø  (aucun opérateur) : le terme peut être absent ou présent

## Exemple

python3 requester.py "+politique +social -president"

```console
1.	0.6644105970267493	CADRES ET EMPLOYÉS COMMUNIENT DANS LA « RELIGION » DU TRAVAIL	{'politique': 1, 'social': 6}
2.	0.6445033866354897	RELANCE DU MOUVEMENT PACIFISTE	{'politique': 8, 'social': 1}
3.	0.6144762981140549	LES IMPASSES D'UN MODÈLE	{'politique': 15, 'social': 1}
```


## Argument obligatoire

argument | description
:-|:-
keywords | les mots-clés de la requête 


## Arguments optionnels

argument | description
:-|:-
-i, --index INDEX | emplacement de l'index
-s {cos, euc}, --similarity {euc, euc} | type de similarité, euclidienne par défaut
-h, --help | affiche l'aide
