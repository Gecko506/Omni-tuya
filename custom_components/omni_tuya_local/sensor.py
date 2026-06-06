from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import OmniTuyaLocalCoordinator
from .entity import OmniTuyaEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coordinator: OmniTuyaLocalCoordinator = hass.data[DOMAIN][entry.entry_id]

    async def add_new_entities() -> None:
        entities = []
        for config in coordinator.store.all().values():
            if config.get("domain") == "sensor":
                dps_map = config.get("dps_map") or {"1": {"name": config.get("name"), "unit": None}}
                for dps_id, desc in dps_map.items():
                    entities.append(OmniTuyaSensor(coordinator, config, str(dps_id), desc if isinstance(desc, dict) else {}))
        async_add_entities(entities)

    coordinator.register_entity_refresh_callback(add_new_entities)
    await add_new_entities()


class OmniTuyaSensor(OmniTuyaEntity, SensorEntity):
    def __init__(self, coordinator, config, dps_id: str, desc: dict) -> None:
        super().__init__(coordinator, config, dps_id)
        self._desc = desc

    @property
    def name(self) -> str:
        return self._desc.get("name") or self.config.get("name") or self.device_id

    @property
    def native_value(self):
        return self.dps(self.dps_id)

    @property
    def native_unit_of_measurement(self) -> str | None:
        return self._desc.get("unit")
