from __future__ import annotations

from homeassistant.components.humidifier import HumidifierEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import OmniTuyaLocalCoordinator
from .entity import OmniTuyaEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coordinator: OmniTuyaLocalCoordinator = hass.data[DOMAIN][entry.entry_id]

    async def add_new_entities() -> None:
        async_add_entities(
            OmniTuyaHumidifier(coordinator, config)
            for config in coordinator.store.all().values()
            if config.get("domain") == "humidifier"
        )

    coordinator.register_entity_refresh_callback(add_new_entities)
    await add_new_entities()


class OmniTuyaHumidifier(OmniTuyaEntity, HumidifierEntity):
    @property
    def name(self) -> str:
        return self.config.get("name") or self.device_id

    @property
    def is_on(self) -> bool | None:
        value = self.dps("1")
        if value is None:
            return None
        return value is True or value == "on"

    @property
    def target_humidity(self) -> int | None:
        value = self.dps("2")
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.async_set_status(self.device_id, True, 1)

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_set_status(self.device_id, False, 1)

    async def async_set_humidity(self, humidity: int) -> None:
        await self.coordinator.async_set_value(self.device_id, 2, humidity)
