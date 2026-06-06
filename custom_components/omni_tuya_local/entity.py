from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEVICE_TYPES, DOMAIN
from .coordinator import OmniTuyaLocalCoordinator


class OmniTuyaEntity(CoordinatorEntity[OmniTuyaLocalCoordinator]):
    _attr_has_entity_name = True

    def __init__(self, coordinator: OmniTuyaLocalCoordinator, config: dict, suffix: str = "") -> None:
        super().__init__(coordinator)
        self.config = config
        self.device_id = config["device_id"]
        self.dps_id = str(suffix or "1")
        unique_suffix = "" if self.dps_id == "1" else f"_{self.dps_id}"
        self._attr_unique_id = f"{DOMAIN}_{self.device_id}{unique_suffix}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.device_id)},
            name=config.get("name") or self.device_id,
            manufacturer="Tuya",
            model=config.get("product_name")
            or DEVICE_TYPES.get(config.get("device_type") or "generic", {}).get("label")
            or config.get("domain")
            or "Tuya Local",
        )

    @property
    def available(self) -> bool:
        return self.coordinator.is_available(self.device_id)

    @property
    def raw_dps(self) -> dict:
        return (self.coordinator.data or {}).get("dps", {}).get(self.device_id, {})

    def dps(self, dps_id: str | int | None = None):
        return self.coordinator.dps_value(self.device_id, str(dps_id or self.dps_id))

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "device_id": self.device_id,
            "host": self.config.get("host"),
            "version": self.config.get("version"),
            "product_name": self.config.get("product_name"),
            "device_type": self.config.get("device_type"),
            "raw_dps": self.raw_dps,
        }

    @property
    def icon(self) -> str | None:
        return DEVICE_TYPES.get(self.config.get("device_type") or "generic", {}).get("icon")
