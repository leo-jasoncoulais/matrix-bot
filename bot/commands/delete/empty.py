import os
import time

import requests

from bot.utils import send
from bot.commands.delete import delete

HOMESERVER = os.getenv("HOMESERVER", "")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")


def _headers():
    return {"Authorization": f"Bearer {ADMIN_TOKEN}"}


def list_all_rooms():
    rooms = []
    from_offset = 0
    limit = 100

    while True:
        url = f"https://{HOMESERVER}/_synapse/admin/v1/rooms"
        params = {"from": from_offset, "limit": limit, "order_by": "name"}
        resp = requests.get(url, headers=_headers(), params=params, timeout=30)
        if resp.status_code != 200:
            raise RuntimeError(
                f"Erreur recuperation rooms ({resp.status_code}): {resp.text}"
            )

        data = resp.json()
        batch = data.get("rooms", [])
        rooms.extend(batch)

        next_token = data.get("next_batch")
        if not batch or next_token is None:
            break
        from_offset = next_token

    return rooms


def delete_room(room_id):
    url = f"https://{HOMESERVER}/_synapse/admin/v2/rooms/{room_id}"
    body = {"block": False, "purge": True, "force_purge": False}
    resp = requests.delete(
        url, json=body, headers=_headers(), timeout=30,
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


def find_empty_remote_rooms(rooms, homeserver_domain):
    return [
        r for r in rooms
        if r.get("joined_members", 0) == 0
        and r["room_id"].split(":")[1] != homeserver_domain
    ]


HELP_TEXT = """\
Usage : /delete empty [--dry-run]

Supprime toutes les rooms sans membre qui ne sont pas sur le homeserver.
Ces rooms sont des donnees inutiles provenant d'autres serveurs.

Options :
  --dry-run   Affiche les rooms qui seraient supprimees sans les supprimer

Exemples :
  /delete empty
  /delete empty --dry-run"""


@delete.command("empty", description="Supprimer les rooms vides externes")
async def cmd_delete_empty(room, event, args):
    if not HOMESERVER or not ADMIN_TOKEN:
        await send(room.room_id, "Variables d'environnement HOMESERVER et ADMIN_TOKEN non configurees.")
        return

    flags = set(args)
    dry_run = "--dry-run" in flags

    await send(room.room_id, "Recuperation de la liste des rooms...")

    try:
        rooms = list_all_rooms()
    except RuntimeError as e:
        await send(room.room_id, str(e))
        return

    homeserver_domain = HOMESERVER.replace("https://", "").replace("http://", "")
    empty_remote = find_empty_remote_rooms(rooms, homeserver_domain)

    if not empty_remote:
        await send(room.room_id, f"Aucune room vide externe trouvee sur {len(rooms)} rooms.")
        return

    lines = [f"{len(empty_remote)} room(s) vide(s) externe(s) trouvee(s) sur {len(rooms)} :"]
    lines.append("")
    for r in empty_remote:
        name = r.get("name") or r.get("canonical_alias") or "(sans nom)"
        lines.append(f"  {name}  ({r['room_id']})")
    lines.append("")

    if dry_run:
        lines.append("Mode dry-run : aucune suppression effectuee.")
        await send(room.room_id, "\n".join(lines))
        return

    await send(room.room_id, "\n".join(lines))
    await send(room.room_id, "Suppression en cours...")

    deleted = 0
    failed = 0
    for r in empty_remote:
        rid = r["room_id"]
        try:
            delete_id = delete_room(rid)
            if delete_id and wait_for_deletion(delete_id):
                deleted += 1
            else:
                failed += 1
        except RuntimeError:
            failed += 1

    await send(room.room_id, f"Termine : {deleted} supprimee(s), {failed} en echec.")
