from bot.utils import send
from bot.commands.delete import delete


@delete.command("message", description="Supprimer un message par son event ID")
async def cmd_delete_message(room, event, args):
    if not args:
        await send(room.room_id, "Usage : /delete message <event_id>")
        return

    event_id = args[0]

    await send(room.room_id, f"Suppression du message {event_id}...")

    from bot import state
    result = await state.client.room_forget(room.room_id)

    # TODO: utiliser l'API admin pour supprimer un message specifique
    await send(room.room_id, "Fonctionnalite pas encore implementee.")
