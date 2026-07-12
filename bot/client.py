import json
import os

from nio import AsyncClient, AsyncClientConfig, LoginResponse

import config


async def build_client():
    """Crée le AsyncClient, restaure une session existante si possible,
    sinon se connecte avec le mot de passe et sauvegarde les identifiants."""

    os.makedirs(config.STORE_PATH, exist_ok=True)

    client_config = AsyncClientConfig(
        store_sync_tokens=True,
        encryption_enabled=True,
    )
    client = AsyncClient(
        config.HOMESERVER,
        config.USER_ID,
        config=client_config,
        store_path=config.STORE_PATH,
    )

    if os.path.exists(config.CREDENTIALS_FILE):
        with open(config.CREDENTIALS_FILE, "r") as f:
            creds = json.load(f)
        client.restore_login(
            user_id=creds["user_id"],
            device_id=creds["device_id"],
            access_token=creds["access_token"],
        )
        print(f"Session restaurée avec le device existant ({creds['device_id']}).")
        return client

    resp = await client.login(config.PASSWORD, device_name=config.DEVICE_NAME)
    if isinstance(resp, LoginResponse):
        with open(config.CREDENTIALS_FILE, "w") as f:
            json.dump({
                "access_token": resp.access_token,
                "user_id": resp.user_id,
                "device_id": resp.device_id,
            }, f)
        print(f"Nouvelle connexion, device_id={resp.device_id} sauvegardé.")
        return client

    print(f"Échec de connexion : {resp}")
    return None
