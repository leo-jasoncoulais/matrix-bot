import sys

from bot import state
from bot.admin import is_server_admin
from bot.registry import command
from bot.utils import send


@command("shutdown", description="Arreter le bot")
async def cmd_shutdown(room, event, args):
    if not is_server_admin(event.sender):
        return
    sys.exit(0)
