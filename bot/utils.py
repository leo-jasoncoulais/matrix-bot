from io import BytesIO

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


async def send_image(room_id, data, content_type="image/gif", filename="image.gif"):
    """Upload un fichier image sur le serveur Matrix puis l'envoie dans la salle."""
    try:
        resp, _ = await state.client.upload(
            BytesIO(data),
            content_type=content_type,
            filename=filename,
            filesize=len(data),
        )
        if hasattr(resp, "content_uri"):
            await state.client.room_send(
                room_id=room_id,
                message_type="m.room.message",
                content={
                    "msgtype": "m.image",
                    "url": resp.content_uri,
                    "body": filename,
                    "info": {"mimetype": content_type},
                },
                ignore_unverified_devices=True,
            )
        else:
            print(f"Erreur upload image : {resp}")
    except Exception as e:
        print(f"Erreur d'envoi image dans {room_id} : {e}")
