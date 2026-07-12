# matrix-bot

## Structure

```
matrix-bot/
├── main.py                 # point d'entrée
├── config.py                # configuration (homeserver, identifiants, admins)
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
        └── shutdown.py
```

## Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Édite `config.py` (homeserver, `USER_ID`) et exporte le mot de passe :

```bash
export MATRIX_BOT_PASSWORD="mon_mot_de_passe"
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
