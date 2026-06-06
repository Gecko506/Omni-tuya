from __future__ import annotations

from homeassistant.components.lock import LockEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import OmniTuyaLocalCoordinator
from .entity import OmniTuyaEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coordinator: OmniTuyaLocalCoordinator = hass.data[DOMAIN][entry.entry_id]

    async def add_new_entities() -> None:
        async_add_entities(
            OmniTuyaLock(coordinator, config)
            for config in coordinator.store.all().values()
            if config.get("domain") == "lock"
        )

    coordinator.register_entity_refresh_callback(add_new_entities)
    await add_new_entities()


class OmniTuyaLock(OmniTuyaEntity, LockEntity):
    @property
    def name(self) -> str:
        return self.config.get("name") or self.device_id

    @property
    def is_locked(self) -> bool | None:
        value = self.dps("1")
        if value is None:
            return None
        return not (value is True or value == "unlocked" or value == "on")

    async def async_lock(self, **kwargs) -> None:
        await self.coordinator.async_set_value(self.device_id, 1, False)

    async def async_unlock(self, **kwargs) -> None:
        await self.coordinator.async_set_value(self.device_id, 1, True)
