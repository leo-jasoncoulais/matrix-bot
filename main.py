import asyncio
import signal
import sys
import time

from nio.schemas import Schemas
Schemas.room_create["properties"]["content"]["properties"]["predecessor"]["required"] = ["room_id"]

from nio import RoomMessageText, MegolmEvent, InviteMemberEvent, SyncResponse

import config
from bot import state, handlers
from bot.client import build_client
from bot.crypto import trust_all_devices
from bot.utils import send

# L'import déclenche l'enregistrement de toutes les commandes
# (voir bot/commands/__init__.py)
import bot.commands


_shutdown_event = asyncio.Event()


def _request_shutdown():
    _shutdown_event.set()


async def shutdown(client):
    if config.NOTIFY_ROOM:
        await send(config.NOTIFY_ROOM, "Bot arrêté")
    await client.close()


async def main():
    client = await build_client()
    if client is None:
        return

    state.set_client(client)

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, _request_shutdown)

    client.add_event_callback(handlers.message_callback, RoomMessageText)
    client.add_event_callback(handlers.encrypted_callback, MegolmEvent)
    client.add_event_callback(handlers.invite_callback, InviteMemberEvent)
    client.add_response_callback(handlers.sync_response_callback, SyncResponse)

    # On ne traite que les messages envoyés après ce point (ignore l'historique)
    handlers.start_time_ms = int(time.time() * 1000)

    # Premier sync pour peupler le device_store, puis on fait confiance aux appareils
    await client.sync(timeout=30000, full_state=True)
    trust_all_devices()

    if config.NOTIFY_ROOM:
        await send(config.NOTIFY_ROOM, "Bot redémarré")

    print("Bot en écoute...")
    try:
        sync_task = asyncio.create_task(client.sync_forever(timeout=30000))
        done, pending = await asyncio.wait(
            [sync_task, asyncio.create_task(_shutdown_event.wait())],
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()
    finally:
        await shutdown(client)
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
