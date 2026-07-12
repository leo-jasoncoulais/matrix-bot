# matrix-bot

## Structure

```
matrix-bot/
├── main.py                 # point d'entrée
├── config.py                # configuration (homeserver, identifiants)
├── admins.json              # liste des IDs admin
├── .env                     # variables d'environnement
├── requirements.txt
└── bot/
    ├── state.py              # référence globale au client Matrix
    ├── registry.py           # registre de commandes (décorateur @command)
    ├── utils.py               # fonctions utilitaires (envoi de message)
    ├── crypto.py              # gestion de la confiance des appareils (E2E)
    ├── client.py               # création/connexion du AsyncClient
    ├── handlers.py             # callbacks d'événements (messages, invitations, chiffrement)
    └── commands/
        ├── __init__.py          # importe chaque commande pour l'enregistrer
        ├── ping.py
        ├── echo.py
        ├── help.py
        ├── shutdown.py
        ├── hierarchy.py
        ├── room_state.py
        └── delete/
            ├── __init__.py
            ├── room.py
            ├── message.py
            └── empty.py
```

## Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration

1. Copie `.env.example` en `.env` et remplis les variables :

```env
HOMESERVER=matrix.org
USER_ID=monbot
PASSWORD=mon_mot_de_passe
ADMIN_TOKEN=mon_token_admin
```

2. Édite `admins.json` avec la liste des user IDs admin :

```json
["@user:matrix.org"]
```

## Lancement

```bash
python main.py
```

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
