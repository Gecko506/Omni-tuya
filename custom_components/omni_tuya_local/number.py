from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import OmniTuyaLocalCoordinator
from .entity import OmniTuyaEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coordinator: OmniTuyaLocalCoordinator = hass.data[DOMAIN][entry.entry_id]

    async def add_new_entities() -> None:
        async_add_entities(
            OmniTuyaNumber(coordinator, config)
            for config in coordinator.store.all().values()
            if config.get("domain") == "number"
        )

    coordinator.register_entity_refresh_callback(add_new_entities)
    await add_new_entities()


class OmniTuyaNumber(OmniTuyaEntity, NumberEntity):
    _attr_native_min_value = 0
    _attr_native_max_value = 1000
    _attr_native_step = 1

    @property
    def name(self) -> str:
        return self.config.get("name") or self.device_id

    @property
    def native_value(self) -> float | None:
        value = self.dps("1")
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_set_value(self.device_id, 1, value)
