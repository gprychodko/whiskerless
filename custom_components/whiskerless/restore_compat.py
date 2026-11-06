"""Read the restore-state cache on both sides of the 2026.11 change.

Home Assistant 2026.11 replaced RestoreStateData.last_states (keyed by
entity_id) with two maps, one keyed by entity registry id, and a getter that
also follows entity_id renames. Older releases only have the dict.
"""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers import restore_state


def stored_state(hass: HomeAssistant, entity_id: str | None) -> restore_state.StoredState | None:
    """The cached state of entity_id, if the restore cache has one."""
    if not entity_id:
        return None
    data = restore_state.async_get(hass)
    if (getter := getattr(data, "async_get_stored_state", None)) is not None:
        return getter(entity_id)
    return data.last_states.get(entity_id)


def move_stored_state(hass: HomeAssistant, old: str, new: str) -> None:
    """Carry a cached state across an entity_id rename.

    Only needed before 2026.11: since then the cache is keyed by registry id,
    which a rename keeps, and the getter rewrites the stored entity_id.
    """
    data = restore_state.async_get(hass)
    cached = getattr(data, "last_states", None)
    if cached is not None and old in cached:
        cached[new] = cached.pop(old)
