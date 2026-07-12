"""
Petit module d'état global.

Le client Matrix (`AsyncClient`) est créé au démarrage dans `bot/client.py`,
mais plusieurs autres modules (commandes, handlers, crypto...) ont besoin d'y
accéder sans dépendre les uns des autres → on centralise la référence ici
pour éviter les imports circulaires.
"""

client = None


def set_client(c):
    global client
    client = c
