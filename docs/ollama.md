# Local recipe and ingredient analysis

The `ollama` service stores models in the `ollama_data` volume. Its API is
available to the backend at `http://ollama:11434`, with no port published on
the host. Analysis runs when recipes are created or updated and when
ingredients are created.

## Prerequisites

The model runs on the CPU. Docker and Docker Compose are required.
Allow enough available RAM for the model and its context, and Internet access
on the first startup to download the model.

## Startup and verification

From the project root, with `.envs/.env.compose` configured:

```sh
make up
```

On startup, the container automatically downloads the model specified by
`RECIPE_AI_MODEL` in `.envs/.env.aimodel` if it is missing from the volume.
This value must match the model configured for the backend.
After the download, the startup script preloads the model into memory.
The health check verifies that the model is present and loaded; the backend
waits for this state (`healthy`) before starting. The first `make up` may
therefore take some time. To follow startup from another terminal:

```sh
export COMPOSE_ENV_FILES=.envs/.env.compose
docker compose logs -f ollama
```

Once startup is complete:

```sh
export COMPOSE_ENV_FILES=.envs/.env.compose
docker compose ps ollama
docker compose exec ollama ollama ps
```

The `PROCESSOR` column in `ollama ps` lets you verify CPU usage.
Preloading at startup avoids loading the model during the first analysis,
as long as it remains in memory.

The context is limited to 4096 tokens, and only one request is processed at a
time to limit memory usage. Also test an incomplete recipe and a recipe whose
steps use missing ingredients. Measure the delay and check for incorrect
judgments: analysis already prevents saving when a request is rejected or
the service is unavailable.

```sh
make down
```

Ollama starts with the other services during `make up` and stops with them
during `make down`. To manage only Ollama:

```sh
export COMPOSE_ENV_FILES=.envs/.env.compose
docker compose up -d --build ollama
docker compose stop ollama
```

`make clean` removes volumes, including downloaded models.

## Backend integration

After the existing validation checks and ingredient name resolution, the
backend calls `/api/chat` with `think: false` and a maximum of 96 tokens.
It validates the returned JSON before modifying any recipe, step, or XP.
Simple and original recipes are accepted; only non-culinary content and
obvious inconsistencies should be rejected.

Analysis errors currently return HTTP 200 with `success: false` and an `error`
message displayed in the form, without saving:

- Model rejection: a reason explaining what needs correcting.
- Ollama unavailable or invalid/truncated response: verification unavailable.
  The connection timeout is 5 seconds and the read timeout is 60 seconds.
- Recipe JSON text exceeding 6000 UTF-8 bytes: recipe too long,
  without silently truncating steps.

When creating an ingredient, the backend uses the same analysis call to check
its culinary relevance, spelling, and category. A rejection or service
unavailability also returns HTTP 200 with `success: false`, without creating
the ingredient.

The backend uses `RECIPE_AI_URL` and `RECIPE_AI_MODEL`, defined in Compose.
It does not send `keep_alive`: `OLLAMA_KEEP_ALIVE` in the Ollama service
controls how long the model stays in memory. The current configuration uses
`OLLAMA_KEEP_ALIVE=-1` to keep the model loaded.

After changing backend variables in Compose, recreate the backend:

```sh
docker compose --env-file .envs/.env.compose up -d --build backend
```

After changing `.envs/.env.aimodel`, recreate Ollama to apply the variables
and preload the model:

```sh
docker compose --env-file .envs/.env.compose up -d --force-recreate ollama
```
