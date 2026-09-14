# Der Die Das API

API pour une application ludique d'apprentissage des articles allemands (der/die/das), avec progression par niveau CECRL (A1 à C2).

## Fonctionnalités

- Inscription avec validation d'adresse email par code OTP
- Connexion / déconnexion via cookie httpOnly (pas de JWT côté client)
- Réinitialisation de mot de passe par OTP
- Rush : sessions de jeu où l'utilisateur doit trouver l'article d'une série de mots
- Suivi de progression par mot (streak de réussite sur plusieurs rushs distincts, démaîtrise en cas d'erreur)
- Dashboard détaillé de progression par niveau
- Passage au niveau supérieur une fois un seuil de maîtrise atteint
- Révision libre des mots (filtrage par niveau et statut de progression, pagination)

## Stack technique

- **Framework** : FastAPI
- **Base de données** : PostgreSQL (Supabase en production)
- **ORM** : SQLAlchemy
- **Validation** : Pydantic
- **Authentification** : cookies httpOnly, mots de passe hashés avec bcrypt (via passlib)
- **Envoi d'email** : SMTP Gmail (validation OTP, réinitialisation de mot de passe)
- **Tests** : pytest, contre une base PostgreSQL locale dédiée

## Structure du projet

> ```
> der-die-das-api/
> ├── app/
> │ ├── main.py 			# point d'entrée FastAPI
> │ ├── config.py 		# configuration, lue depuis .env
> │ ├── database.py 		# connexion PostgreSQL, session SQLAlchemy
> │ ├── models/ 			# tables SQLAlchemy
> │ ├── schemas/ 			# schémas Pydantic (entrée/sortie API)
> │ ├── routers/ 			# endpoints, groupés par domaine
> │ ├── services/ 		# logique métier
> │ ├── core/ 			# sécurité, dépendances d'authentification
> │ └── utils/ 			# fonctions transverses (génération d'id, dates, email)
> ├── scripts/
> │ ├── create_tables.py 	# création des tables en base
> │ └── load_data.py 		# chargement du dataset de mots
> ├── data/ 				# dataset final (mot, article, niveau, traductions)
> ├── raw_data/ 			# sources brutes utilisées pour préparer les données
> ├── notebook/ 			# notebook de préparation des données
> ├── tests/ 				# suite de tests pytest
> ├── .env 				# variables d'environnement (non versionné)
> └── requirements.txt
> ```

## Prérequis

- Python 3.11+
- Une base PostgreSQL (locale, ou un projet Supabase)
- Un compte Gmail avec un mot de passe d'application (validation en deux étapes activée)

## Installation

```Shell
# Windows
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

```Shell
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Créer un fichier `.env` à la racine, sur le modèle `.env.example`

## Variables d'environnement

| Variable                                                                          | Description                                                                                         |
| --------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| `DATABASE_URL`                                                                  | URL de connexion PostgreSQL (production/développement)                                             |
| `TEST_DATABASE_URL`                                                             | URL de connexion PostgreSQL utilisée par les tests                                                 |
| `SECRET_KEY`                                                                    | Clé secrète de l'application                                                                      |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM` | Configuration de l'envoi d'email (OTP)                                                              |
| `OTP_EXPIRY_MINUTES`                                                            | Durée de validité d'un code OTP (par défaut 10)                                                  |
| `OTP_RESEND_COOLDOWN_SECONDS`                                                   | Délai minimum entre deux envois d'OTP (par défaut 60)                                             |
| `SESSION_EXPIRY_DAYS`                                                           | Durée de validité d'une session (par défaut 7)                                                   |
| `MASTERY_STREAK_THRESHOLD`                                                      | Nombre de réussites sur des rushs distincts pour maîtriser un mot (par défaut 3)                 |
| `LEVEL_COMPLETION_THRESHOLD`                                                    | Proportion de mots maîtrisés pour valider un niveau (par défaut 0.85)                            |
| `RUSH_SIZE`                                                                     | Nombre de mots proposés par rush (par défaut 10)                                                  |
| `ENVIRONMENT`                                                                   | `development` ou `production`                                                                   |
| `COOKIE_SECURE`                                                                 | `true` en production (HTTPS), `false` en développement local                                   |
| `COOKIE_SAMESITE`                                                               | `lax` en développement, `none` en production si front et API sont sur des domaines différents |
| `ALLOWED_ORIGINS`                                                               | Liste des origines autorisées pour le CORS, séparées par des virgules                            |

## Base de données

Les tables sont créées via un script dédié (pas de migrations versionnées pour l'instant) :

```bash
python -m scripts.create_tables
```

Le dataset de mots (voir `notebook/`) doit ensuite être chargé :

```bash
python -m scripts.load_data
```

### Sources des données

- Dataset des noms allemands avec article et genre : [gambolputty/german-nouns](https://github.com/gambolputty/german-nouns) (GitHub, consulté le 13 septembre 2026)
- Wortlisten du Goethe-Institut, version TSV par niveau (A1, A2, B1) : [ilkermeliksitki/goethe-institute-wordlist](https://github.com/ilkermeliksitki/goethe-institute-wordlist) (GitHub, consulté le 13 septembre 2026)
- PDF officiels Goethe-Institut : [A1](https://www.goethe.de/pro/relaunch/prf/sw/Goethe-Zertifikat_A1_Fit1_Wortliste.pdf), [A2](https://lmsspada.kemdikbud.go.id/mod/resource/view.php?id=108392), [B1](https://www.goethe.de/pro/relaunch/prf/da/Goethe-Zertifikat_B1_Wortliste.pdf)
- Traductions française et anglaise générées via Google Sheets (`GOOGLETRANSLATE`)

## Lancer l'application

```bash
uvicorn app.main:app --reload
```

Documentation interactive disponible sur `http://localhost:8000/docs`.

## Lancer les tests

```bash
pytest tests/ -v
```

Les tests s'exécutent contre `TEST_DATABASE_URL`, une base isolée recréée à chaque test.

## Aperçu des endpoints

### Authentification (`/auth`)

| Méthode | Route                     | Description                                   |
| -------- | ------------------------- | --------------------------------------------- |
| POST     | `/auth/register`        | Inscription, envoi d'un OTP de validation     |
| POST     | `/auth/verify-otp`      | Validation de l'adresse email                 |
| POST     | `/auth/resend-otp`      | Renvoi d'un OTP de validation                 |
| POST     | `/auth/login`           | Connexion, pose le cookie de session httpOnly |
| POST     | `/auth/logout`          | Déconnexion                                  |
| POST     | `/auth/forgot-password` | Demande de réinitialisation de mot de passe  |
| POST     | `/auth/reset-password`  | Réinitialisation effective du mot de passe   |

### Utilisateur (`/users`)

| Méthode | Route                       | Description                                            |
| -------- | --------------------------- | ------------------------------------------------------ |
| GET      | `/users/me`               | Profil de l'utilisateur connecté                      |
| GET      | `/users/me/dashboard`     | Progression détaillée sur le niveau actuel           |
| POST     | `/users/me/advance-level` | Passage au niveau supérieur (si le seuil est atteint) |

### Rush (`/rush`)

| Méthode | Route                      | Description                                             |
| -------- | -------------------------- | ------------------------------------------------------- |
| POST     | `/rush/start`            | Démarre un rush, renvoie une sélection de mots        |
| POST     | `/rush/answer`           | Soumet une réponse pour un mot du rush en cours        |
| POST     | `/rush/{rush_id}/finish` | Termine le rush, renvoie le score et les mots à revoir |

### Mots (`/words`)

| Méthode | Route      | Description                                                            |
| -------- | ---------- | ---------------------------------------------------------------------- |
| GET      | `/words` | Liste paginée des mots, filtrable par niveau et statut de progression |

## Points connus, à traiter plus tard

- Environ 122 mots des Wortlisten Goethe n'ont pas encore de correspondance dans le dataset d'articles (à vérifier/compléter manuellement)
- Les mots de niveau B2 à C2 n'ont pas encore de source de données fiable identifiée
- Pas encore de migrations de base de données versionnées (Alembic), le schéma est encore amené à évoluer
