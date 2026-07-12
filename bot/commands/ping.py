from bot.registry import command
from bot.utils import send


@command("ping", description="Verifier que le bot est en ligne")
async def cmd_ping(room, event, args):
    await send(room.room_id, "pong 🏓")
