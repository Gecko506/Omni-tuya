from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import OmniTuyaLocalCoordinator
from .entity import OmniTuyaEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coordinator: OmniTuyaLocalCoordinator = hass.data[DOMAIN][entry.entry_id]

    async def add_new_entities() -> None:
        entities = [
            OmniTuyaSwitch(coordinator, config)
            for config in coordinator.store.all().values()
            if config.get("domain") == "switch"
        ]
        async_add_entities(entities)

    coordinator.register_entity_refresh_callback(add_new_entities)
    await add_new_entities()


class OmniTuyaSwitch(OmniTuyaEntity, SwitchEntity):
    @property
    def name(self) -> str:
        return self.config.get("name") or self.device_id

    @property
    def is_on(self) -> bool | None:
        value = self.dps("1")
        if value is None:
            return None
        return value is True or value == "on"

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.async_set_status(self.device_id, True, 1)

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_set_status(self.device_id, False, 1)
