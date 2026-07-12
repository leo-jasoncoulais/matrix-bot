from bot import state


async def send(room_id, text):
    """Envoie un message texte, en ignorant les appareils non vérifiés
    (nécessaire en environnement chiffré)."""
    try:
        await state.client.room_send(
            room_id=room_id,
            message_type="m.room.message",
            content={"msgtype": "m.text", "body": text},
            ignore_unverified_devices=True,
        )
    except Exception as e:
        print(f"Erreur d'envoi dans {room_id} : {e}")
