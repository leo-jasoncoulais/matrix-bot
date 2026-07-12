import os

from bot import state
from bot.registry import command
from bot.utils import send
from config import ADMINS


@command("shutdown", description="Arreter le bot")
async def cmd_shutdown(room, event, args):
    if event.sender not in ADMINS:
        return
    await send(room.room_id, "Arrêt du bot...")
    await state.client.close()
    os._exit(0)
