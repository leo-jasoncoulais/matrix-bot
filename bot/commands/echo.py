from bot.registry import command
from bot.utils import send


@command("echo", description="Repeter un message")
async def cmd_echo(room, event, args):
    if not args:
        await send(room.room_id, "Usage : !echo <texte>")
        return
    await send(room.room_id, " ".join(args))
