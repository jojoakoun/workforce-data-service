# Sécurité et priorisation des risques

Ce document présente les mesures de sécurité présentes dans le prototype, les risques connus et les améliorations prioritaires pour une utilisation en production.

Le prototype a une portée limitée. Il ne doit pas être considéré comme une configuration de production complète.

## Mesures présentes dans le prototype

### Requêtes SQL paramétrées

Les requêtes SQL utilisent des paramètres plutôt que de concaténer directement les valeurs reçues.

Cette approche réduit le risque d’injection SQL.

L’implémentation se trouve principalement dans :

```text
app/queries.py
app/loader.py
```

### Validation des données

Le pipeline valide les données avant leur chargement dans PostgreSQL.

Il vérifie notamment :

- la présence des feuilles attendues;
- la présence des colonnes requises;
- les types de poste autorisés;
- les noms des ministères;
- les valeurs négatives;
- les périodes;
- les doublons.

L’implémentation se trouve dans :

```text
app/validation.py
app/processing.py
```

### Contraintes PostgreSQL

La base protège également l’intégrité des données.

Les principales protections sont :

- clés primaires;
- clé étrangère;
- unicité du nom anglais de référence;
- unicité de la clé métier;
- interdiction des `headcount` négatifs;
- interdiction des ETP négatifs.

Le schéma se trouve dans :

```text
sql/schema.sql
```

Cette approche protège les données à deux niveaux :

```text
validation Python
        ↓
contraintes PostgreSQL
```

### Configuration par variable d’environnement

La connexion PostgreSQL utilise :

```text
DATABASE_URL
```

La valeur réelle est stockée localement dans :

```text
.env
```

Le fichier `.env` est exclu du dépôt Git.

Le dépôt contient :

```text
.env.example
```

pour documenter la configuration attendue sans publier les informations locales de connexion.

## Risques connus

### 1. Absence d’authentification et d’autorisation

Le prototype ne contrôle pas l’identité de la personne qui appelle l’API.

Dans un environnement exposé, une personne pouvant atteindre le service pourrait interroger les endpoints.

**Priorité : élevée**

Une version de production devrait utiliser le mécanisme d’identité approuvé par l’organisation et définir clairement les utilisateurs ou systèmes autorisés à accéder aux données.

### 2. Gestion des secrets

Le prototype utilise un fichier `.env` pour le développement local.

Ce mécanisme est adapté au prototype, mais une production devrait utiliser un gestionnaire de secrets approuvé.

**Priorité : élevée**

Les mots de passe, chaînes de connexion et autres secrets ne devraient pas être stockés dans le dépôt ou directement dans les fichiers de configuration déployés.

### 3. Chiffrement des communications

Le serveur local fonctionne en HTTP pendant le développement.

**Priorité : élevée**

Une version de production devrait utiliser TLS pour protéger :

- les communications entre les clients et l’API;
- les connexions entre l’application et PostgreSQL.

### 4. Privilèges de la base de données

Une application de production ne devrait pas utiliser un compte PostgreSQL administrateur.

**Priorité : élevée**

Je créerais un compte propre à l’application avec uniquement les droits nécessaires pour lire et écrire dans les objets requis.

Le principe serait :

```text
minimum de permissions nécessaires
```

### 5. Journalisation et surveillance

Le prototype affiche les principales étapes de traitement, mais il ne fournit pas une infrastructure complète de journalisation et de surveillance.

**Priorité : moyenne**

Une version de production devrait suivre :

- les erreurs de l’API;
- les échecs d’importation;
- les erreurs de validation;
- la durée des importations;
- les erreurs PostgreSQL;
- les événements nécessaires au soutien opérationnel.

Les journaux ne devraient pas contenir inutilement des secrets ou des données sensibles.

### 6. Protection contre les abus

Le prototype ne contient pas de limite de requêtes.

**Priorité : moyenne**

Si l’API était exposée à un plus grand nombre d’utilisateurs ou à un réseau moins contrôlé, j’évaluerais :

- la limitation du débit;
- les délais d’exécution;
- les limites de taille des requêtes;
- les limites de connexion;
- la surveillance des comportements anormaux.

### 7. Sécurité des dépendances

Le projet dépend de plusieurs bibliothèques Python.

**Priorité : moyenne**

Une chaîne de livraison de production devrait analyser régulièrement :

- les dépendances vulnérables;
- les versions obsolètes;
- le code source;
- les changements introduits par les demandes de tirage.

Des outils SAST, des analyses de dépendances et des mises à jour régulières pourraient être intégrés au processus CI.

## Priorisation

Je traiterais d’abord les risques pouvant permettre un accès non autorisé aux données ou au système.

L’ordre serait donc :

```text
1. authentification et autorisation
2. protection des secrets
3. chiffrement des communications
4. privilèges minimaux PostgreSQL
5. journalisation et surveillance
6. protection contre les abus
7. analyses automatisées des dépendances et du code
```

Cette priorisation se base sur l’impact potentiel d’une exploitation et sur la probabilité d’exposition dans un environnement de production.

## Validation des entrées API

FastAPI vérifie le type du paramètre `department_id` et du filtre `year` à partir de leurs annotations Python.

Les valeurs sont ensuite transmises aux requêtes SQL sous forme de paramètres.

Une version de production pourrait appliquer des règles supplémentaires, par exemple :

- une plage d’années acceptable;
- une liste explicite de valeurs `tenure`;
- des limites supplémentaires sur les paramètres futurs.

Ces validations supplémentaires seraient ajoutées selon les besoins réels du service.

## Sécurité du processus d’importation

Le fichier source n’est jamais modifié.

Les données sont inspectées et validées avant le chargement.

Les valeurs invalides connues ne sont pas transformées arbitrairement.

Par exemple, le `headcount` négatif observé est converti en valeur manquante plutôt qu’en valeur positive supposée.

Cette approche favorise la traçabilité et évite de présenter comme certaine une correction qui ne peut pas être confirmée.

## Limites actuelles

Le prototype ne comprend pas :

```text
authentification
autorisation
TLS configuré dans l’application
gestionnaire de secrets
rate limiting
journalisation centralisée
SAST automatisé
DAST automatisé
analyse automatique des dépendances
déploiement de production
```

Ces éléments sont considérés comme des améliorations de production et non comme des fonctionnalités déjà implémentées.