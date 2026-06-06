from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import OmniTuyaLocalCoordinator
from .entity import OmniTuyaEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coordinator: OmniTuyaLocalCoordinator = hass.data[DOMAIN][entry.entry_id]

    async def add_new_entities() -> None:
        async_add_entities(
            OmniTuyaBinarySensor(coordinator, config)
            for config in coordinator.store.all().values()
            if config.get("domain") == "binary_sensor"
        )

    coordinator.register_entity_refresh_callback(add_new_entities)
    await add_new_entities()


class OmniTuyaBinarySensor(OmniTuyaEntity, BinarySensorEntity):
    @property
    def name(self) -> str:
        return self.config.get("name") or self.device_id

    @property
    def is_on(self) -> bool | None:
        value = self.dps("1")
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        return str(value).lower() in {"1", "true", "on", "open", "motion", "detected"}
