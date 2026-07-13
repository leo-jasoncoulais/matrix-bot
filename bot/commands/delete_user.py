from bot.admin import delete_user, is_server_admin
from bot.registry import command
from bot.utils import send
from config import HOMESERVER


@command("delete_user", description="Supprimer un compte du homeserver")
async def cmd_delete_user(room, event, args):
    if not is_server_admin(event.sender):
        return

    if not args:
        await send(room.room_id, "Usage: !delete_user <user>")
        return

    raw_id = args[0]

    if raw_id.startswith("@") and ":" in raw_id:
        user_id = raw_id
    else:
        user_id = f"@{raw_id}:{HOMESERVER.removeprefix('https://')}"

    err = delete_user(user_id)

    if err is None:
        await send(room.room_id, f"Compte {user_id} supprimé.")
    else:
        await send(room.room_id, f"Échec de la suppression : {err}")
