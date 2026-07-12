"""
Importer ce package suffit à enregistrer toutes les commandes : chaque
sous-module utilise le décorateur @command(...) qui s'exécute dès l'import.

Pour ajouter une commande simple :
1. crée bot/commands/ma_commande.py avec une fonction décorée @command("xxx")
2. ajoute `from . import ma_commande` ci-dessous

Pour ajouter un groupe de sous-commandes :
1. crée bot/commands/mon_groupe/__init__.py avec un Group
2. crée les sous-modules dans le dossier
3. ajoute `from . import mon_groupe` ci-dessous
"""

from . import ping
from . import echo
from . import shutdown
from . import hierarchy
from . import room_state
from . import help
from . import delete
