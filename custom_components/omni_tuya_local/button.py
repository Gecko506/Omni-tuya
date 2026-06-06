from __future__ import annotations

import asyncio

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import OmniTuyaLocalCoordinator
from .entity import OmniTuyaEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coordinator: OmniTuyaLocalCoordinator = hass.data[DOMAIN][entry.entry_id]

    async def add_new_entities() -> None:
        async_add_entities(
            OmniTuyaButton(coordinator, config)
            for config in coordinator.store.all().values()
            if config.get("domain") == "button"
        )

    coordinator.register_entity_refresh_callback(add_new_entities)
    await add_new_entities()


class OmniTuyaButton(OmniTuyaEntity, ButtonEntity):
    @property
    def name(self) -> str:
        return self.config.get("name") or self.device_id

    async def async_press(self) -> None:
        await self.coordinator.async_set_status(self.device_id, True, 1)
        await asyncio.sleep(0.25)
        await self.coordinator.async_set_status(self.device_id, False, 1)
