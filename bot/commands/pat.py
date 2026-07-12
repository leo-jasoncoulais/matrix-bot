import aiohttp

from bot.registry import command
from bot.utils import send, send_image


@command("pat", description="Verifier que le bot est en ligne")
async def cmd_pat(room, event, args):
    url = "https://klipy.com/gifs/cat-girl-head-pat"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.read()
                await send_image(room.room_id, data, content_type="image/gif", filename="pat.gif")
            else:
                await send(room.room_id, "Erreur lors du t\u00e9l\u00e9chargement du GIF.")
