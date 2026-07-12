import os

import requests

from bot.registry import command
from bot.utils import send

HOMESERVER = os.getenv("HOMESERVER", "")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")


def _headers():
    return {"Authorization": f"Bearer {ADMIN_TOKEN}"}


HELP_TEXT = """\
Usage : /room-state <room_id>

Affiche l'etat detaille d'une room (nom, membres, type, etat...).

Exemple :
  /room-state !abc123:matrix.org"""


@command("room-state", description="Verifier l'etat detaille d'une room")
async def cmd_room_state(room, event, args):
    if not HOMESERVER or not ADMIN_TOKEN:
        await send(room.room_id, "Variables d'environnement HOMESERVER et ADMIN_TOKEN non configurees.")
        return

    if not args:
        await send(room.room_id, HELP_TEXT)
        return

    target_room_id = args[0]

    await send(room.room_id, f"Recuperation des infos de {target_room_id}...")

    url = f"https://{HOMESERVER}/_synapse/admin/v1/rooms/{target_room_id}"
    resp = requests.get(url, headers=_headers(), timeout=30)
    if resp.status_code != 200:
        await send(room.room_id, f"Impossible de recuperer les infos ({resp.status_code}). Room inexistante ?")
        return

    info = resp.json()
    name = info.get("name") or info.get("canonical_alias") or "(sans nom)"
    topic = info.get("topic") or "(aucun)"
    room_version = info.get("room_version", "?")
    members = info.get("joined_members", "?")
    joined_local = info.get("joined_local_members", "?")
    room_type = info.get("room_type") or "(standard)"
    creator = info.get("creator", "?")
    canonical_alias = info.get("canonical_alias") or "(aucun)"
    federable = info.get("m.federate", "?")

    lines = [
        f"=== Etat de la room ===",
        f"",
        f"Room ID    : {target_room_id}",
        f"Nom        : {name}",
        f"Alias      : {canonical_alias}",
        f"Topic      : {topic}",
        f"Type       : {room_type}",
        f"Version    : {room_version}",
        f"Createur   : {creator}",
        f"Federation  : {'oui' if federable else 'non'}",
        f"Membres    : {members} (locaux : {joined_local})",
    ]

    state_resp = requests.get(
        f"https://{HOMESERVER}/_synapse/admin/v1/rooms/{target_room_id}/state",
        headers=_headers(),
        timeout=30,
    )
    if state_resp.status_code == 200:
        state_events = state_resp.json().get("state", [])
        lines.append(f"Etat        : {len(state_events)} evenement(s)")

        join_rules = None
        encryption = False
        history_visibility = None
        for ev in state_events:
            etype = ev.get("type")
            content = ev.get("content", {})
            if etype == "m.room.join_rules":
                join_rules = content.get("join_rule", "?")
            elif etype == "m.room.encryption":
                encryption = True
            elif etype == "m.room.history_visibility":
                history_visibility = content.get("history_visibility", "?")

        if join_rules:
            lines.append(f"Acces       : {join_rules}")
        if encryption:
            lines.append(f"Chiffrement : active")
        if history_visibility:
            lines.append(f"Historique  : {history_visibility}")

    await send(room.room_id, "\n".join(lines))
