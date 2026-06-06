from __future__ import annotations

from homeassistant.components.light import ColorMode, LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_BRIGHTNESS
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import OmniTuyaLocalCoordinator
from .entity import OmniTuyaEntity
from .util import ha_to_tuya_brightness, tuya_to_ha_brightness


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coordinator: OmniTuyaLocalCoordinator = hass.data[DOMAIN][entry.entry_id]

    async def add_new_entities() -> None:
        async_add_entities(
            OmniTuyaLight(coordinator, config)
            for config in coordinator.store.all().values()
            if config.get("domain") == "light"
        )

    coordinator.register_entity_refresh_callback(add_new_entities)
    await add_new_entities()


class OmniTuyaLight(OmniTuyaEntity, LightEntity):
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_color_mode = ColorMode.BRIGHTNESS

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
    def brightness(self) -> int | None:
        value = self.dps("3")
        if value is None:
            return None
        try:
            return tuya_to_ha_brightness(int(value))
        except (TypeError, ValueError):
            return None

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.async_set_status(self.device_id, True, 1)
        if ATTR_BRIGHTNESS in kwargs:
            await self.coordinator.async_set_value(self.device_id, 3, ha_to_tuya_brightness(kwargs[ATTR_BRIGHTNESS]))

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_set_status(self.device_id, False, 1)
