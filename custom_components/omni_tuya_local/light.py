from __future__ import annotations

from homeassistant.components.light import ATTR_BRIGHTNESS, ColorMode, LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import OmniTuyaLocalCoordinator
from .entity import OmniTuyaEntity
from .util import ha_to_tuya_brightness, tuya_to_ha_brightness


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coordinator: OmniTuyaLocalCoordinator = hass.data[DOMAIN][entry.entry_id]

    async def add_new_entities() -> None:
        entities = []
        for config in coordinator.store.all().values():
            if config.get("domain") == "light":
                for dps_id, name in _light_dps(config, coordinator):
                    entities.append(OmniTuyaLight(coordinator, config, dps_id, name))
        async_add_entities(entities)

    coordinator.register_entity_refresh_callback(add_new_entities)
    await add_new_entities()


class OmniTuyaLight(OmniTuyaEntity, LightEntity):
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_color_mode = ColorMode.BRIGHTNESS

    def __init__(self, coordinator, config: dict, dps_id: str = "1", channel_name: str | None = None) -> None:
        super().__init__(coordinator, config, dps_id)
        self._channel_name = channel_name

    @property
    def name(self) -> str:
        if self._channel_name:
            return self._channel_name
        return self.config.get("name") or self.device_id

    @property
    def is_on(self) -> bool | None:
        value = self.dps(self.dps_id)
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
        await self.coordinator.async_set_status(self.device_id, True, int(self.dps_id))
        if ATTR_BRIGHTNESS in kwargs:
            await self.coordinator.async_set_value(self.device_id, 3, ha_to_tuya_brightness(kwargs[ATTR_BRIGHTNESS]))

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_set_status(self.device_id, False, int(self.dps_id))


def _light_dps(config: dict, coordinator: OmniTuyaLocalCoordinator) -> list[tuple[str, str | None]]:
    dps_map = config.get("dps_map") or {}
    channels: list[tuple[str, str | None]] = []
    for dps_id, desc in dps_map.items():
        if str(dps_id).isdigit():
            name = desc.get("name") if isinstance(desc, dict) else None
            channels.append((str(dps_id), name))

    raw_dps = (coordinator.data or {}).get("dps", {}).get(config.get("device_id"), {})
    for dps_id, value in raw_dps.items():
        if isinstance(value, bool) and str(dps_id).isdigit() and (str(dps_id), None) not in channels:
            channels.append((str(dps_id), None))

    if not channels:
        channels.append(("1", None))
    return sorted(channels, key=lambda item: int(item[0]))
