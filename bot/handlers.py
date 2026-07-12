from nio import MatrixRoom, RoomMessageText, MegolmEvent, InviteMemberEvent

from bot import state, registry
from bot.registry import PREFIX
from bot.crypto import trust_all_devices

# Rempli par main.py juste avant sync_forever : les messages antérieurs
# à ce timestamp (historique rejoué au démarrage) sont ignorés.
start_time_ms = 0


async def message_callback(room: MatrixRoom, event: RoomMessageText):
    if event.sender == state.client.user_id:
        return

    if event.server_timestamp < start_time_ms:
        return

    # Ignore les éditions de message (m.replace) pour ne pas redéclencher une commande
    relates_to = event.source.get("content", {}).get("m.relates_to", {})
    if relates_to.get("rel_type") == "m.replace":
        return

    body = event.body.strip()
    if not body or not body.startswith(PREFIX):
        return

    parts = body.split()
    command_name = parts[0].lower()
    args = parts[1:]

    try:
        await registry.dispatch(command_name, room, event, args)
    except Exception as e:
        print(f"Erreur lors de l'exécution de {command_name} dans {room.room_id} : {e}")


async def encrypted_callback(room: MatrixRoom, event: MegolmEvent):
    """Se déclenche quand un message chiffré ne peut pas être déchiffré.
    On demande alors la clé manquante à l'appareil émetteur."""
    print(f"⚠️ Message non déchiffrable dans {room.room_id}, demande de clé en cours...")
    try:
        await state.client.request_room_key(event)
    except Exception as e:
        print(f"Impossible de demander la clé : {e}")


async def invite_callback(room: MatrixRoom, event: InviteMemberEvent):
    result = await state.client.join(room.room_id)
    if hasattr(result, "room_id"):
        print(f"Salon rejoint : {room.room_id}")
    else:
        print(f"Impossible de rejoindre {room.room_id} : {result}")


async def sync_response_callback(response):
    # Réappelé à chaque sync pour absorber les nouveaux appareils au fil de l'eau
    trust_all_devices()
