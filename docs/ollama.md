# Analyse locale des recettes

Le service `ollama` conserve les modèles
dans le volume `ollama_data`. Son API est accessible au backend sur
`http://ollama:11434`, sans port publié sur la machine.
L'analyse est utilisée à la création et à la modification des recettes.
Ollama doit tourner et Qwen3 4B doit être téléchargé avant de publier.

## Prérequis

Le GPU doit être visible avec `nvidia-smi`. Docker doit disposer du NVIDIA
Container Toolkit : https://docs.ollama.com/docker.
Sous WSL2, utiliser le pilote NVIDIA Windows compatible WSL ; ne pas installer
un pilote graphique Linux dans la distribution WSL.

## Démarrage et vérification

Depuis la racine du projet, avec `.envs/.env.compose` configuré :

```sh
make up
make ai-test
```

Au démarrage, le conteneur télécharge automatiquement le modèle défini par
`RECIPE_AI_MODEL` dans `.envs/.env.aimodel` s'il manque dans le volume.
La valeur doit correspondre au modèle configuré pour le backend.
Le conteneur devient sain (`healthy`) lorsque le modèle est disponible.
`make up` rend la main avant la fin du téléchargement : attendre l'état
`healthy` avec `docker compose ps ollama` avant de lancer `make ai-test`.
`make ai-pull` reste disponible pour télécharger manuellement le modèle.

Le téléchargement de Qwen3 4B représente environ 2,5 Go. Le premier appel
inclut le chargement du modèle. La colonne `PROCESSOR` de `ollama ps` permet
de vérifier l'utilisation du GPU ; viser `100% GPU`.

Le test utilise l'API avec `think: false`, un verdict JSON court et une limite
de 96 tokens générés. Il affiche la durée totale et le temps de chargement.
Relancer `make ai-test` pour mesurer une réponse avec le modèle déjà chargé.
Le script nécessite Python 3 et un accès direct aux réseaux Docker depuis
l'hôte Linux/WSL. Pour tester un autre texte :

```sh
COMPOSE_ENV_FILES=.envs/.env.compose python3 scripts/test_recipe_ai.py 'Recette à vérifier'
```

Le contexte est limité à 4096 tokens et une seule requête est traitée à la
fois pour limiter l'utilisation de la VRAM. Tester également une recette
incomplète et une recette dont les étapes utilisent des ingrédients absents.
Mesurer le délai et vérifier les erreurs de jugement avant de bloquer des
publications sur la base de l'analyse.

```sh
make down
```

Ollama démarre avec les autres services lors de `make up` et s'arrête avec
eux lors de `make down`. Les commandes `make ai-up` et `make ai-stop`
restent disponibles pour gérer uniquement Ollama.
`make clean` supprime les volumes, y compris les modèles téléchargés.

## Intégration au backend

Après les validations existantes et la résolution des noms d'ingrédients,
le backend appelle `/api/chat` avec `think: false` et 96 tokens maximum.
Il vérifie le JSON reçu avant toute modification de recette, étape ou XP.
Les recettes simples et originales sont acceptées ; seuls le contenu non
culinaire et les incohérences évidentes doivent être refusés.

- Refus : HTTP 422, avec un motif affiché dans le formulaire existant.
- Ollama indisponible, délai de lecture supérieur à 15 secondes ou réponse
  invalide/tronquée : HTTP 503, sans enregistrement.
- Texte JSON à analyser supérieur à 6000 octets UTF-8 : HTTP 400, sans
  troncature silencieuse des étapes.

Le backend utilise `RECIPE_AI_URL` et `RECIPE_AI_MODEL`, définis dans le
Compose. Il n'envoie pas `keep_alive` : `OLLAMA_KEEP_ALIVE` dans le service
Ollama contrôle la durée de maintien en mémoire. Le script de test conserve
son réglage indépendant de 10 minutes.

Après changement de la configuration, recréer le backend :

```sh
docker compose --env-file .envs/.env.compose up -d --build backend
```

Tests isolés, sans Vault ni PostgreSQL, avec SQLite en mémoire :

```sh
PYTHONPATH=src/backend python3 -m unittest discover -s tests -p test_recipe_analysis.py -v
```
