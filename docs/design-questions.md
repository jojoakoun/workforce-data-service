# Questions de conception

Ce document répond aux trois questions de conception de l’exercice.

Les réponses décrivent les changements que j’apporterais au prototype si le volume, les sources ou les besoins des analystes évoluaient.

# Question 1 — Passage à des dizaines de millions d’enregistrements

Si le volume passait de quelques milliers à des dizaines de millions d’enregistrements, je conserverais l’architecture générale, mais je modifierais principalement le processus d’importation et l’accès aux données.

## Importation par lots

Le prototype actuel utilise pandas et convient au volume fourni.

À beaucoup plus grande échelle, je ne chargerais pas l’ensemble du jeu de données en mémoire.

Je traiterais les données par lots :

```text
source
  ↓
lecture par lots
  ↓
validation
  ↓
transformation
  ↓
chargement PostgreSQL
```

Cette approche réduit l’utilisation de la mémoire et permet de reprendre plus facilement une importation interrompue.

## Chargement en masse

Le prototype actuel privilégie une implémentation simple.

À grande échelle, j’utiliserais les mécanismes de chargement en masse de PostgreSQL, notamment `COPY`, plutôt que des insertions individuelles.

Je pourrais également charger les données dans une table de staging avant de les valider et de les transférer vers les tables finales.

Le flux deviendrait :

```text
source
  ↓
staging
  ↓
validation
  ↓
tables finales
```

Cette séparation faciliterait les contrôles de qualité et la reprise après erreur.

## Indexation

J’ajouterais des index basés sur les requêtes réellement utilisées.

Les candidats naturels seraient notamment :

```text
department_id
period
tenure
```

et certaines combinaisons utilisées fréquemment par les filtres.

Je vérifierais les plans d’exécution PostgreSQL avant d’ajouter des index supplémentaires.

Un index accélère certaines lectures, mais augmente aussi le coût des insertions et l’espace disque utilisé.

## Partitionnement

Avec des dizaines de millions d’enregistrements, j’évaluerais un partitionnement de `workforce_records` par période, par exemple par année.

Le partitionnement pourrait réduire la quantité de données examinée pour les requêtes limitées à une période donnée.

Je ne l’ajouterais cependant qu’après avoir confirmé qu’il améliore les requêtes réelles.

## Séparation des traitements

L’API et les importations devraient fonctionner comme des processus indépendants.

Une longue importation ne devrait pas bloquer l’API utilisée par les analystes.

Les importations pourraient être exécutées par un travailleur ou un service planifié distinct.

## API

Pour les endpoints pouvant retourner beaucoup de données, j’ajouterais :

```text
pagination
limites de requêtes
timeouts
mise en cache lorsque pertinente
```

Les agrégations fréquemment utilisées pourraient également être pré-calculées si les mesures montrent que leur calcul à la demande devient trop coûteux.

## Surveillance

Je mesurerais :

```text
durée des importations
nombre de lignes traitées
erreurs de validation
requêtes SQL lentes
temps de réponse de l’API
utilisation de la base
```

Ces mesures permettraient d’optimiser les parties qui posent réellement problème plutôt que de complexifier l’architecture à l’avance.

---

# Question 2 — Synchronisation avec une API externe

La nouvelle source fournit des mises à jour quotidiennes et peut réviser des données historiques.

Cette situation demande plus qu’un simple remplacement du fichier Excel par un appel HTTP. Le système doit préserver la qualité des données et permettre aux analystes de comprendre les changements.

## 2.1 Automatiser la synchronisation tout en assurant la qualité des données

Je séparerais l’extraction, la validation et la publication des données.

Le processus serait :

```text
API externe
   ↓
récupération
   ↓
zone de staging
   ↓
validation
   ↓
comparaison avec les données existantes
   ↓
publication
```

### Synchronisation planifiée

Un processus planifié appellerait l’API une fois par jour.

Chaque exécution enregistrerait au minimum :

```text
date et heure de synchronisation
source
statut
nombre d’enregistrements reçus
nombre d’enregistrements ajoutés
nombre d’enregistrements révisés
erreurs rencontrées
```

Une synchronisation en échec ne devrait pas remplacer les données actuellement disponibles.

### Validation avant publication

Les nouvelles données passeraient par les mêmes types de contrôles que le prototype :

```text
structure
types
valeurs requises
plages acceptables
références de ministères
doublons
règles métier
```

Les données invalides seraient isolées avant leur publication.

### Révisions historiques

Je ne considérerais pas une observation existante comme immuable.

Lorsqu’une valeur historique change, le système devrait identifier la différence entre :

```text
ancienne valeur
nouvelle valeur
```

Je conserverais également des informations permettant de savoir quand une révision a été reçue.

Pour des analyses devant rester reproductibles, une solution de production pourrait conserver un historique des versions ou des instantanés.

Cela permettrait de distinguer :

```text
valeur actuellement publiée
```

de :

```text
valeur utilisée lors d’une analyse antérieure
```

### Idempotence

Chaque synchronisation devrait être idempotente.

Recevoir deux fois le même contenu ne devrait pas créer deux copies du même enregistrement.

### Gestion des erreurs externes

L’API externe appartient à une autre organisation. Le système doit donc prévoir :

```text
timeouts
indisponibilité temporaire
réponses incomplètes
changements de schéma
limites de débit
```

Je conserverais la dernière version valide des données lorsqu’une synchronisation échoue.

Les nouvelles données ne seraient publiées qu’après validation.

---

## 2.2 Intégrer les changements aux flux de travail des analystes

Je commencerais par comprendre comment les analystes utilisent actuellement les données.

Je chercherais notamment à savoir :

```text
quels scripts ils utilisent
quelles colonnes ils attendent
quels modèles Power BI dépendent des données
quelles analyses publiées doivent rester reproductibles
comment ils traitent actuellement les révisions
```

L’objectif serait d’éviter de casser leurs outils existants lorsque la source change.

### Maintenir un contrat stable

Même si la source externe change, je chercherais à garder le schéma utilisé par les analystes aussi stable que possible.

Le service agirait comme une couche d’adaptation entre :

```text
API externe
```

et :

```text
outils des analystes
```

Une modification de la source ne devrait pas automatiquement devenir une modification de l’interface offerte aux analystes.

### Communiquer les révisions

Les révisions historiques doivent être visibles.

J’ajouterais des informations permettant de savoir :

```text
quelles données ont changé
quand elles ont changé
quelle période est touchée
```

Pour un changement important, je communiquerais avec les analystes avant son déploiement lorsque leurs scripts ou résultats publiés peuvent être affectés.

### Reproductibilité

Une analyse publiée doit pouvoir expliquer quelles données ont été utilisées.

Selon les besoins, je proposerais :

```text
des versions de jeux de données
des dates de dernière mise à jour
des instantanés
un historique des révisions
```

Cela permettrait à un analyste de reproduire une analyse antérieure même si la source officielle a ensuite été révisée.

### Documentation

Je documenterais :

```text
le calendrier de mise à jour
les règles de révision
les champs disponibles
les changements de schéma
la signification des valeurs
les méthodes d’accès
```

Les analystes devraient pouvoir comprendre le comportement du service sans avoir à lire son code.

---

## 2.3 Révision de la pull request de synchronisation

Je commencerais par les risques pouvant compromettre les données ou la sécurité, puis j’examinerais la maintenabilité et les performances.

### Priorité 1 — Exactitude et intégrité des données

Je vérifierais d’abord :

```text
la correspondance entre les champs externes et notre modèle
les règles de validation
la gestion des révisions historiques
la gestion des doublons
l’idempotence
les transactions
le comportement en cas d’échec partiel
```

Une synchronisation qui corrompt silencieusement les données serait plus grave qu’une synchronisation simplement lente.

### Priorité 2 — Sécurité

Je vérifierais :

```text
la gestion des secrets
l’utilisation de TLS
la validation des données externes
les requêtes SQL paramétrées
les permissions de la base
les journaux
les dépendances ajoutées
```

Une réponse provenant d’une API externe doit être considérée comme une entrée non fiable jusqu’à sa validation.

### Priorité 3 — Fiabilité

Je vérifierais le comportement lorsque :

```text
l’API externe est indisponible
une requête expire
la réponse est incomplète
la structure change
une synchronisation est relancée
```

Le système devrait échouer de manière visible et conserver les dernières données valides.

### Priorité 4 — Tests

Je chercherais des tests couvrant au minimum :

```text
synchronisation normale
réexécution de la même synchronisation
nouveaux enregistrements
révisions historiques
données invalides
échec de l’API externe
échec de la base de données
```

Les tests devraient vérifier le comportement observable et les règles métier importantes.

### Priorité 5 — Maintenabilité

Je vérifierais ensuite :

```text
la simplicité du code
la séparation des responsabilités
les noms
les commentaires utiles
la duplication
la cohérence avec l’architecture existante
```

Je demanderais des changements lorsque la complexité ajoutée n’est pas nécessaire au problème.

### Priorité 6 — Performance

Je vérifierais finalement :

```text
le nombre d’appels à l’API externe
le nombre de requêtes SQL
la taille des lots
les transactions
les index utilisés
```

J’optimiserais en priorité les problèmes mesurés ou clairement susceptibles de devenir coûteux.

---

# Question 3 — Utilisation directe avec Power BI et Python

Si les analystes souhaitent utiliser directement les données avec Power BI et Python, je chercherais d’abord à rendre l’accès stable, documenté et prévisible.

## Vues adaptées aux analystes

Je créerais des vues SQL présentant des données déjà jointes et faciles à comprendre.

Par exemple, une vue pourrait contenir :

```text
period
source
department
department_short_name
tenure
headcount
fte
```

Les analystes n’auraient alors pas besoin de connaître les clés internes ou de reconstruire les mêmes jointures dans chaque outil.

## Accès en lecture seule

Je créerais un rôle PostgreSQL dédié aux analystes.

Ce rôle aurait uniquement des permissions de lecture sur les vues ou tables nécessaires.

Il ne pourrait pas :

```text
modifier les données
supprimer les données
modifier le schéma
```

Cette séparation réduirait le risque de modification accidentelle.

## Power BI

Pour Power BI, je fournirais :

```text
une source PostgreSQL stable
des vues documentées
des noms de colonnes cohérents
des types de données prévisibles
une indication de la dernière mise à jour
```

Selon le volume et les besoins, j’évaluerais aussi :

```text
Import mode
DirectQuery
```

Le choix dépendrait de la fréquence de mise à jour, du volume et des performances nécessaires.

## Python

Pour Python, je fournirais des exemples simples montrant comment :

```text
se connecter
exécuter une requête
charger les résultats dans pandas
filtrer par période
filtrer par ministère
```

Je pourrais également fournir un petit notebook ou script d’exemple.

L’objectif ne serait pas de créer une nouvelle bibliothèque complexe, mais de réduire le temps nécessaire pour commencer une analyse.

## Métadonnées

J’ajouterais une documentation des champs contenant :

```text
nom du champ
description
type
source
valeurs possibles
règle de calcul
traitement des valeurs manquantes
```

La règle de calcul des ETP trimestriels devrait notamment être explicitement documentée.

## Fraîcheur des données

Les analystes devraient pouvoir déterminer rapidement quand les données ont été mises à jour.

J’ajouterais donc des métadonnées telles que :

```text
last_updated_at
source_updated_at
data_version
```

si le service évoluait vers des mises à jour régulières.

## Révisions historiques

Si les données peuvent être révisées, les analystes devraient pouvoir savoir quelles versions ont été utilisées.

Selon les besoins, j’ajouterais :

```text
un historique des versions
des instantanés
une date de validité
une date de réception
```

Cela améliorerait la reproductibilité des analyses publiées.

## Documentation et exemples

Je fournirais enfin une documentation courte avec des exemples adaptés aux outils réellement utilisés par les analystes.

Le but serait de leur permettre de répondre rapidement à trois questions :

```text
Comment accéder aux données ?
Que signifie chaque champ ?
Quelle version des données suis-je en train d’utiliser ?
```

Ces fonctionnalités amélioreraient l’expérience des analystes sans les obliger à comprendre l’implémentation interne du service.