from __future__ import annotations

from homeassistant.components.climate import ClimateEntity, ClimateEntityFeature, HVACMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import OmniTuyaLocalCoordinator
from .entity import OmniTuyaEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coordinator: OmniTuyaLocalCoordinator = hass.data[DOMAIN][entry.entry_id]

    async def add_new_entities() -> None:
        async_add_entities(
            OmniTuyaClimate(coordinator, config)
            for config in coordinator.store.all().values()
            if config.get("domain") == "climate"
        )

    coordinator.register_entity_refresh_callback(add_new_entities)
    await add_new_entities()


class OmniTuyaClimate(OmniTuyaEntity, ClimateEntity):
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT, HVACMode.COOL, HVACMode.AUTO]

    @property
    def name(self) -> str:
        return self.config.get("name") or self.device_id

    @property
    def hvac_mode(self) -> HVACMode:
        power = self.dps("1")
        if power is False or power == "off":
            return HVACMode.OFF
        mode = str(self.dps("2") or "auto").lower()
        return {
            "heat": HVACMode.HEAT,
            "cool": HVACMode.COOL,
            "auto": HVACMode.AUTO,
        }.get(mode, HVACMode.AUTO)

    @property
    def current_temperature(self):
        return self.dps("3")

    @property
    def target_temperature(self):
        return self.dps("4")

    async def async_set_temperature(self, **kwargs) -> None:
        if "temperature" in kwargs:
            await self.coordinator.async_set_value(self.device_id, 4, kwargs["temperature"])

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        if hvac_mode == HVACMode.OFF:
            await self.coordinator.async_set_status(self.device_id, False, 1)
            return
        await self.coordinator.async_set_status(self.device_id, True, 1)
        await self.coordinator.async_set_value(self.device_id, 2, hvac_mode.value)
