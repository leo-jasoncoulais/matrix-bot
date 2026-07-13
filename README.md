# matrix-bot

## Installation

```bash
cp .env.example .env
# Remplis le fichier .env avec tes identifiants
docker compose up -d
```

## Configuration

1. Copie `.env.example` en `.env` et remplis les variables :

```env
HOMESERVER=matrix.org
USER_ID=@monbot:matrix.org
PASSWORD=mon_mot_de_passe
ADMIN_TOKEN=mon_token_admin
DOCKER_GID=999
```

2. Édite `admins.json` avec la liste des user IDs admin :

```json
["@user:matrix.org"]
```

- `DOCKER_GID` : ID du groupe docker de l'hôte (obtenir avec `getent group docker`).

## Ajouter une commande

1. Crée `bot/commands/ma_commande.py` :

```python
from bot.registry import command
from bot.utils import send

@command("!ma_commande")
async def cmd_ma_commande(room, event, args):
    await send(room.room_id, "réponse")
```

2. Enregistre-la dans `bot/commands/__init__.py` :

```python
from . import ma_commande
```

Rien d'autre à toucher — le décorateur se charge du reste.
