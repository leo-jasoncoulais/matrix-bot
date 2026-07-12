from bot import state


def trust_all_devices():
    """
    Fait confiance à tous les appareils connus, y compris les nouveaux.
    ⚠️ Désactive la vérification anti-MITM d'E2E. Pratique pour un bot,
    à éviter si tu manipules un jour des données sensibles.
    """
    for user_id, devices in state.client.device_store.items():
        for device_id, olm_device in devices.items():
            if not olm_device.verified:
                state.client.verify_device(olm_device)
