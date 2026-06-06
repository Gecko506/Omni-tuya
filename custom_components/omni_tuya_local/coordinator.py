from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DEFAULT_POLL_INTERVAL, DOMAIN
from .device import OmniTuyaDevice
from .storage import TuyaDeviceStore

_LOGGER = logging.getLogger(__name__)


class OmniTuyaLocalCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, store: TuyaDeviceStore) -> None:
        self.entry = entry
        self.store = store
        self.devices: dict[str, OmniTuyaDevice] = {}
        self._entity_refresh_callbacks: list[callback] = []
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_POLL_INTERVAL),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        await self._ensure_devices()
        dps_by_device: dict[str, dict[str, Any]] = {}
        availability: dict[str, bool] = {}
        for device_id, device in self.devices.items():
            dps_by_device[device_id] = await device.async_status()
            availability[device_id] = device.available
        return {
            "devices": self.store.all(),
            "dps": dps_by_device,
            "available": availability,
        }

    async def _ensure_devices(self) -> None:
        configured = self.store.all()
        for device_id, config in configured.items():
            if device_id not in self.devices and config.get("enabled", True):
                self.devices[device_id] = OmniTuyaDevice(self.hass, config)
        for device_id in list(self.devices):
            if device_id not in configured or not configured[device_id].get("enabled", True):
                self.devices.pop(device_id, None)

    async def async_add_device(self, config: dict[str, Any]) -> dict[str, Any]:
        stored = await self.store.add(config)
        self.devices[stored["device_id"]] = OmniTuyaDevice(self.hass, stored)
        await self.async_request_refresh()
        self._notify_entity_refresh()
        return stored

    async def async_add_devices(self, configs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        stored = await self.store.add_many(configs)
        for config in stored:
            self.devices[config["device_id"]] = OmniTuyaDevice(self.hass, config)
        await self.async_request_refresh()
        self._notify_entity_refresh()
        return stored

    async def async_remove_device(self, device_id: str) -> bool:
        self.devices.pop(device_id, None)
        removed = await self.store.remove(device_id)
        await self.async_request_refresh()
        self._notify_entity_refresh()
        return removed

    async def async_reload_devices(self) -> None:
        self.devices.clear()
        await self.store.async_load()
        await self.async_request_refresh()
        self._notify_entity_refresh()

    async def async_shutdown(self) -> None:
        self.devices.clear()

    def register_entity_refresh_callback(self, cb) -> None:
        self._entity_refresh_callbacks.append(cb)

    def _notify_entity_refresh(self) -> None:
        for cb in list(self._entity_refresh_callbacks):
            self.hass.async_create_task(cb())

    def get_device_config(self, device_id: str) -> dict[str, Any] | None:
        return self.store.get(device_id)

    def dps_value(self, device_id: str, dps_id: str = "1") -> Any:
        return (self.data or {}).get("dps", {}).get(device_id, {}).get(str(dps_id))

    def is_available(self, device_id: str) -> bool:
        return bool((self.data or {}).get("available", {}).get(device_id))

    async def async_set_status(self, device_id: str, value: bool, dps_id: int = 1) -> bool:
        await self._ensure_devices()
        device = self.devices.get(device_id)
        if not device:
            return False
        ok = await device.async_set_status(value, dps_id)
        await asyncio.sleep(0)
        await self.async_request_refresh()
        return ok

    async def async_set_value(self, device_id: str, dps_id: int, value: Any) -> bool:
        await self._ensure_devices()
        device = self.devices.get(device_id)
        if not device:
            return False
        ok = await device.async_set_value(dps_id, value)
        await asyncio.sleep(0)
        await self.async_request_refresh()
        return ok
