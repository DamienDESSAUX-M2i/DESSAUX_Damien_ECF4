# DESSAUX_Damien_ECF4

ECF4 de la formation Développeur Concepteur en Science des Donnée de M2i.

## Données

### Téléchargement des données

1. Créez un dossier `data` à la racine du projet.
2. Téléchargez l'archive https://www.kaggle.com/api/v1/datasets/download/jillanisofttech/fake-or-real-news.
3. Extrayez le contenue de l'archive dans le dossier `data`.

### Structure des données

| Colonne | Type | Description |
| :- | :- | :- |
| `title` | str | Titre de l'article |
| `text` | str | Corps de l'article (non utilisé dans ce sujet) |
| `label` | str | `REAL` ou `FAKE` |

## Prérequis

- Docker et Docker Compose
- Python 3.13+
- Git
- UV

## Installation

### Cloner le projet depuis GitHub.

Clonner le projet depuis GitHub en éxécuant la commande :

```bash
git clone https://github.com/DamienDESSAUX-M2i/DESSAUX_Damien_ECF4.git
```

### Créer un environement virtuel et installer les dépendances.

Créez un environnement virtuel et installez les dépendances en éxécutant la commande :

```bash
uv sync
```

Puis téléchargez le modèle linguistique `en_core_web_sm` de `spaCy` en éxécutant la commande :

```bash
uv run -m spacy download en_core_web_sm 
```

### Variables d'environnement

Créez un fichier .env à la racine du projet contenant les varialbes d'environnement suivantes :

```yaml
API_NAME = "fake_news_predictor"
DEBUG = True
API_PREFIX = "/api"

DATABASE_PATH = "data/api.db"

VECTORIZER_PATH = "models/tf_idf_vectorizer"
MODEL_PATH = "models/model_dense.keras"

SECRET_KEY = "my-super-secret-key"
ALGORITHM = "HS256"
ITERATIONS = 100000
ACCESS_TOKEN_EXPIRE_MINUTES = 30

LOG_LEVEL = "INFO"
LOG_PATH = "api/log/api.log"
```