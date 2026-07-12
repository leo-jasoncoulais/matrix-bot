import os
import requests
from bot.registry import command
from bot.utils import send
from config import ADMINS

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
                f"Erreur récupération rooms ({resp.status_code}): {resp.text}"
            )

        data = resp.json()
        batch = data.get("rooms", [])
        rooms.extend(batch)

        next_token = data.get("next_batch")
        if not batch or next_token is None:
            break
        from_offset = next_token

    return rooms


def get_room_state_type(room_id):
    url = f"https://{HOMESERVER}/_synapse/admin/v1/rooms/{room_id}/state"
    resp = requests.get(url, headers=_headers(), timeout=30)
    if resp.status_code != 200:
        return None
    for event in resp.json().get("state", []):
        if event.get("type") == "m.room.create":
            return event.get("content", {}).get("type")
    return None


def get_direct_children(room_id):
    children = []
    params = {"limit": 100, "max_depth": 1}
    url = f"https://{HOMESERVER}/_matrix/client/v1/rooms/{room_id}/hierarchy"

    while True:
        resp = requests.get(url, headers=_headers(), params=params, timeout=30)
        if resp.status_code != 200:
            raise RuntimeError(
                f"Impossible de lire la hiérarchie de {room_id} "
                f"({resp.status_code}): {resp.text}"
            )

        data = resp.json()
        for room in data.get("rooms", []):
            if room["room_id"] == room_id:
                continue
            children.append({
                "room_id": room["room_id"],
                "name": room.get("name") or room.get("canonical_alias") or "(sans nom)",
                "is_space": room.get("room_type") == "m.space",
                "num_joined_members": room.get("num_joined_members", 0),
            })

        next_batch = data.get("next_batch")
        if not next_batch:
            break
        params["from"] = next_batch

    return children


def build_hierarchy(rooms):
    all_room_info = {}
    for r in rooms:
        rid = r["room_id"]
        room_type = r.get("room_type")
        if room_type is None:
            room_type = get_room_state_type(rid)
        all_room_info[rid] = {
            "name": r.get("name") or r.get("canonical_alias") or "(sans nom)",
            "is_space": room_type == "m.space",
            "num_joined_members": r.get("joined_members", 0),
        }

    spaces = [rid for rid, info in all_room_info.items() if info["is_space"]]

    children_map = {}
    child_of = {}

    for space_id in spaces:
        children = get_direct_children(space_id)
        children_map[space_id] = children
        for child in children:
            child_of.setdefault(child["room_id"], []).append(space_id)
            all_room_info.setdefault(child["room_id"], {
                "name": child["name"],
                "is_space": child["is_space"],
                "num_joined_members": child["num_joined_members"],
            })

    roots = [sid for sid in spaces if sid not in child_of]

    return roots, all_room_info, children_map


def format_tree(room_id, all_room_info, children_map, prefix="", is_last=True, visited=None):
    if visited is None:
        visited = set()

    info = all_room_info.get(room_id, {"name": room_id, "is_space": False, "num_joined_members": "?"})
    connector = "└── " if is_last else "├── "
    icon = "🗂️ " if info["is_space"] else "💬 "
    members = info.get("num_joined_members", "?")
    lines = [f"{prefix}{connector}{icon}{info['name']}  ({room_id})  [{members} membre(s)]"]

    if room_id in visited:
        lines.append(f"{prefix}{'    ' if is_last else '│   '}    ↳ (déjà affiché, cycle évité)")
        return lines
    visited.add(room_id)

    children = children_map.get(room_id, [])
    new_prefix = prefix + ("    " if is_last else "│   ")
    for i, child in enumerate(children):
        lines.extend(
            format_tree(
                child["room_id"], all_room_info, children_map,
                prefix=new_prefix, is_last=(i == len(children) - 1),
                visited=visited,
            )
        )

    return lines


async def _send_lines(room_id, lines, chunk_size=4000):
    buffer = ""
    for line in lines:
        if len(buffer) + len(line) + 1 > chunk_size:
            if buffer:
                await send(room_id, buffer)
            buffer = line
        else:
            buffer = f"{buffer}\n{line}" if buffer else line
    if buffer:
        await send(room_id, buffer)


@command("hierarchy", description="Afficher l'arbre des spaces et rooms")
async def cmd_hierarchy(room, event, args):

    if event.sender not in ADMINS:
        await send(room.room_id, f"Vous n'êtes pas administrateur de https://{HOMESERVER} !")
        return

    if not HOMESERVER or not ADMIN_TOKEN:
        await send(room.room_id, "❌ Variables d'environnement HOMESERVER et ADMIN_TOKEN non configurées.")
        return

    await send(room.room_id, f"→ Récupération de la liste des rooms sur https://{HOMESERVER}...")

    try:
        rooms = list_all_rooms()
    except RuntimeError as e:
        await send(room.room_id, f"❌ {e}")
        return

    lines = [f"{len(rooms)} room(s) trouvée(s) au total.", ""]

    try:
        roots, all_room_info, children_map = build_hierarchy(rooms)
    except RuntimeError as e:
        await send(room.room_id, f"❌ {e}")
        return

    lines.append("=== Hiérarchie des spaces ===")
    lines.append("")
    if not roots:
        lines.append("(aucun space racine trouvé)")
    for i, root_id in enumerate(roots):
        lines.extend(format_tree(root_id, all_room_info, children_map, is_last=(i == len(roots) - 1)))
        lines.append("")

    referenced = set()
    for children in children_map.values():
        for c in children:
            referenced.add(c["room_id"])
    space_ids = {rid for rid, info in all_room_info.items() if info["is_space"]}

    orphans = [
        rid for rid in all_room_info
        if rid not in referenced and rid not in space_ids
    ]
    lines.append("=== Rooms hors de tout space ===")
    lines.append("")
    if not orphans:
        lines.append("(aucune)")
    for rid in orphans:
        info = all_room_info[rid]
        lines.append(f"💬 {info['name']}  ({rid})  [{info['num_joined_members']} membre(s)]")
    lines.append("")

    await _send_lines(room.room_id, lines)
