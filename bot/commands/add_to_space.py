import os

from bot import state
from bot.registry import command
from bot.utils import send

HOMESERVER = os.getenv("HOMESERVER", "")

HELP_TEXT = """\
Usage : !add-to-space <space_id> <room_id>

Associe une room a un space en envoyant un evenement m.space.child.
Le bot doit etre present dans le space.

Exemples :
  !add-to-space !space123:example.com !room456:example.com
  !add-to-space !space123:example.com !room456:example.com via example.com other.com"""


@command("add-to-space", description="Associer une room a un space")
async def cmd_add_to_space(room, event, args):
    if not HOMESERVER:
        await send(room.room_id, "Variable d'environnement HOMESERVER non configuree.")
        return

    if len(args) < 2:
        await send(room.room_id, HELP_TEXT)
        return

    space_id = args[0]
    child_room_id = args[1]

    if len(args) >= 3:
        via = args[2:]
    else:
        via = [HOMESERVER.split(":")[-1]]

    content = {
        "via": via,
        "auto_join": False,
    }

    await send(room.room_id, f"Ajout de {child_room_id} dans le space {space_id}...")

    resp = await state.client.room_put_state(
        room_id=space_id,
        event_type="m.space.child",
        state_key=child_room_id,
        content=content,
    )

    if hasattr(resp, "event_id"):
        await send(room.room_id, f"Room {child_room_id} associee au space {space_id} avec succes.")
    else:
        await send(room.room_id, f"Erreur lors de l'ajout : {resp}")
