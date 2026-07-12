import asyncio
import time

from nio.schemas import Schemas
Schemas.room_create["properties"]["content"]["properties"]["predecessor"]["required"] = ["room_id"]

from nio import RoomMessageText, MegolmEvent, InviteMemberEvent, SyncResponse

from bot import state, handlers
from bot.client import build_client
from bot.crypto import trust_all_devices

# L'import déclenche l'enregistrement de toutes les commandes
# (voir bot/commands/__init__.py)
import bot.commands  # noqa: F401


async def main():
    client = await build_client()
    if client is None:
        return

    state.set_client(client)

    client.add_event_callback(handlers.message_callback, RoomMessageText)
    client.add_event_callback(handlers.encrypted_callback, MegolmEvent)
    client.add_event_callback(handlers.invite_callback, InviteMemberEvent)
    client.add_response_callback(handlers.sync_response_callback, SyncResponse)

    # On ne traite que les messages envoyés après ce point (ignore l'historique)
    handlers.start_time_ms = int(time.time() * 1000)

    # Premier sync pour peupler le device_store, puis on fait confiance aux appareils
    await client.sync(timeout=30000, full_state=True)
    trust_all_devices()

    print("Bot en écoute...")
    await client.sync_forever(timeout=30000)


if __name__ == "__main__":
    asyncio.run(main())
    