import os

from bot import state
from bot.admin import is_server_admin
from bot.registry import command
from bot.utils import send


@command("shutdown", description="Arreter le bot")
async def cmd_shutdown(room, event, args):
    if not is_server_admin(event.sender):
        return
    await send(room.room_id, "Arrêt du bot...")
    await state.client.close()
    os._exit(0)
