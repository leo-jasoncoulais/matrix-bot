import os
import time

import requests

from bot.utils import send
from bot.commands.delete import delete

HOMESERVER = os.getenv("HOMESERVER", "")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")


def _headers():
    return {"Authorization": f"Bearer {ADMIN_TOKEN}"}


def get_room_info(room_id):
    url = f"https://{HOMESERVER}/_synapse/admin/v1/rooms/{room_id}"
    resp = requests.get(url, headers=_headers(), timeout=30)
    if resp.status_code == 200:
        return resp.json()
    return None


def delete_room(room_id, purge=True, force=False):
    url = f"https://{HOMESERVER}/_synapse/admin/v2/rooms/{room_id}"
    body = {
        "block": False,
        "purge": purge,
        "force_purge": force,
    }
    resp = requests.delete(
        url,
        json=body,
        headers=_headers(),
        timeout=30,
    )
    if resp.status_code != 200:
        raise RuntimeError(
            f"Erreur suppression {room_id} ({resp.status_code}): {resp.text}"
        )
    return resp.json().get("delete_id")


def wait_for_deletion(delete_id, timeout=120):
    url = f"https://{HOMESERVER}/_synapse/admin/v2/rooms/delete_status/{delete_id}"
    start = time.time()
    while time.time() - start < timeout:
        resp = requests.get(url, headers=_headers(), timeout=30)
        if resp.status_code == 200:
            status = resp.json().get("status")
            if status == "complete":
                return True
            if status == "failed":
                return False
        time.sleep(2)
    return False


HELP_TEXT = """\
Usage : /delete room <room_id> [options]

Options :
  --no-purge   Bloque la room sans purger les donnees de la BDD
  --force      Force la purge meme si l'etat de la room est incoherent

Exemples :
  /delete room !abc123:matrix.org
  /delete room !abc123:matrix.org --force
  /delete room !abc123:matrix.org --no-purge"""


@delete.command("room", description="Supprimer une room")
async def cmd_delete_room(room, event, args):
    if not HOMESERVER or not ADMIN_TOKEN:
        await send(room.room_id, "Variables d'environnement HOMESERVER et ADMIN_TOKEN non configurees.")
        return

    if not args:
        await send(room.room_id, HELP_TEXT)
        return

    room_id = args[0]
    flags = set(args[1:])
    purge = "--no-purge" not in flags
    force = "--force" in flags

    await send(room.room_id, f"Recuperation des infos de {room_id}...")

    info = get_room_info(room_id)
    if info:
        name = info.get("name") or info.get("canonical_alias") or "(sans nom)"
        members = info.get("joined_members", "?")
        await send(room.room_id, f"Nom : {name}\nMembres : {members}")
    else:
        await send(room.room_id, "Impossible de recuperer les infos (room inexistante ou deja supprimee ?)")
        return

    await send(room.room_id, f"Suppression de {room_id} en cours...")

    try:
        delete_id = delete_room(room_id, purge=purge, force=force)
    except RuntimeError as e:
        await send(room.room_id, str(e))
        return

    if not delete_id:
        await send(room.room_id, "Echec de la demande de suppression.")
        return

    ok = wait_for_deletion(delete_id)
    if ok:
        await send(room.room_id, f"Room {room_id} supprimee avec succes.")
    else:
        await send(room.room_id, f"La suppression a rencontre un probleme (delete_id={delete_id}), verifie les logs Synapse.")
