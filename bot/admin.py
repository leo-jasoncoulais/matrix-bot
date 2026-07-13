import os

import requests

HOMESERVER = os.getenv("HOMESERVER", "")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")


def _headers():
    return {"Authorization": f"Bearer {ADMIN_TOKEN}"}


def _base():
    return f"https://{HOMESERVER}"


def is_server_admin(user_id: str) -> bool:
    try:
        resp = requests.get(
            f"{_base()}/_synapse/admin/v1/users/{user_id}/admin",
            headers=_headers(),
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json().get("admin", False)
    except Exception:
        pass
    return False


def set_server_admin(user_id: str, admin: bool) -> bool:
    try:
        resp = requests.put(
            f"{_base()}/_synapse/admin/v1/users/{user_id}/admin",
            headers=_headers(),
            json={"admin": admin},
            timeout=10,
        )
        return resp.status_code == 200
    except Exception:
        return False


def delete_user(user_id: str) -> str | None:
    """Supprime un utilisateur. Retourne None si ok, sinon le message d'erreur."""
    try:
        resp = requests.delete(
            f"{_base()}/_synapse/admin/v2/users/{user_id}",
            headers=_headers(),
            timeout=10,
        )
        if resp.status_code == 200:
            return None
        return f"Erreur {resp.status_code} : {resp.text}"
    except Exception as e:
        return str(e)
