from bot.registry import command
from bot.utils import send


@command("pat", description="Verifier que le bot est en ligne")
async def cmd_pat(room, event, args):
    await send(room.room_id, "https://images-ext-1.discordapp.net/external/Yh1VRYl64zXqDRghL2uK4GSg-I3VWwhn3q6M_O0-tK8/https/static.klipy.com/ii/f87f46a2c5aeaeed4c68910815f73eaf/30/71/1RW0uSwf.mp4")
