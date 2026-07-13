import secrets
import string

from nio import RegisterResponse

from bot import state
from bot.admin import is_server_admin, set_server_admin
from bot.registry import command
from bot.utils import send
from config import HOMESERVER


@command("register", description="Créer un compte sur le homeserver")
async def cmd_register(room, event, args):
    if not is_server_admin(event.sender):
        return

    if not args:
        await send(room.room_id, "Usage: !register <user> [--admin]")
        return

    is_admin = "--admin" in args
    username = [a for a in args if a != "--admin"]

    if not username:
        await send(room.room_id, "Usage: !register <user> [--admin]")
        return

    user_id = f"@{username[0]}:{HOMESERVER.removeprefix('https://')}"

    password = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(20))

    resp = await state.client.register(user_id, password)

    if isinstance(resp, RegisterResponse):
        if is_admin:
            set_server_admin(resp.user_id, True)
        role = "admin" if is_admin else "classique"
        await send(room.room_id, f"Compte créé ({role}) :\n• user_id : {resp.user_id}\n• password : {password}")
    else:
        await send(room.room_id, f"Échec de la création : {resp}")
