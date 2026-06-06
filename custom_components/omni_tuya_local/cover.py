from __future__ import annotations

from homeassistant.components.cover import CoverEntity, CoverEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import OmniTuyaLocalCoordinator
from .entity import OmniTuyaEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coordinator: OmniTuyaLocalCoordinator = hass.data[DOMAIN][entry.entry_id]

    async def add_new_entities() -> None:
        async_add_entities(
            OmniTuyaCover(coordinator, config)
            for config in coordinator.store.all().values()
            if config.get("domain") == "cover"
        )

    coordinator.register_entity_refresh_callback(add_new_entities)
    await add_new_entities()


class OmniTuyaCover(OmniTuyaEntity, CoverEntity):
    _attr_supported_features = CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE | CoverEntityFeature.STOP

    @property
    def name(self) -> str:
        return self.config.get("name") or self.device_id

    @property
    def is_closed(self) -> bool | None:
        value = self.dps("1")
        if value is None:
            return None
        return value in ("close", "closed", False)

    async def async_open_cover(self, **kwargs) -> None:
        await self.coordinator.async_set_value(self.device_id, 1, "open")

    async def async_close_cover(self, **kwargs) -> None:
        await self.coordinator.async_set_value(self.device_id, 1, "close")

    async def async_stop_cover(self, **kwargs) -> None:
        await self.coordinator.async_set_value(self.device_id, 1, "stop")
