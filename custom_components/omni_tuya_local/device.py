from __future__ import annotations

import asyncio
import logging
from typing import Any

from homeassistant.core import HomeAssistant

from .models import TuyaDeviceConfig

_LOGGER = logging.getLogger(__name__)


class OmniTuyaDevice:
    def __init__(self, hass: HomeAssistant, config: dict[str, Any]) -> None:
        self.hass = hass
        self.config = TuyaDeviceConfig.from_dict(config)
        self.device_id = self.config.device_id
        self._tuya = None
        self._available = False
        self._last_dps: dict[str, Any] = {}
        self._lock = asyncio.Lock()

    @property
    def available(self) -> bool:
        return self._available

    @property
    def dps(self) -> dict[str, Any]:
        return dict(self._last_dps)

    def _build_tuya(self):
        import tinytuya

        if self.config.node_id and self.config.gateway_id:
            parent = tinytuya.Device(
                dev_id=self.config.gateway_id,
                address=self.config.gateway_host or self.config.host,
                local_key=self.config.gateway_local_key or self.config.local_key,
                version=float(self.config.version or 3.3),
            )
            device = tinytuya.Device(dev_id=self.device_id, cid=self.config.node_id, parent=parent)
        else:
            device = tinytuya.Device(
                dev_id=self.device_id,
                address=self.config.host,
                local_key=self.config.local_key,
                version=float(self.config.version or 3.3),
            )
        device.set_socketPersistent(False)
        return device

    def _device(self):
        if self._tuya is None:
            self._tuya = self._build_tuya()
        return self._tuya

    async def async_status(self) -> dict[str, Any]:
        async with self._lock:
            try:
                raw = await self.hass.async_add_executor_job(self._device().status)
                if raw and isinstance(raw, dict) and "dps" in raw:
                    self._last_dps = dict(raw["dps"])
                    self._available = True
                    return self.dps
                self._available = False
                return self.dps
            except Exception as err:
                _LOGGER.debug("Poll error for %s: %s", self.device_id, err)
                self._available = False
                self._tuya = None
                return self.dps

    async def async_set_status(self, value: bool, dps_id: int = 1) -> bool:
        async with self._lock:
            try:
                await self.hass.async_add_executor_job(lambda: self._device().set_status(value, dps_id))
                self._last_dps[str(dps_id)] = value
                self._available = True
                return True
            except Exception as err:
                _LOGGER.error("Command failed for %s dps %s: %s", self.device_id, dps_id, err)
                self._available = False
                self._tuya = None
                return False

    async def async_set_value(self, dps_id: int, value: Any) -> bool:
        async with self._lock:
            try:
                await self.hass.async_add_executor_job(lambda: self._device().set_value(dps_id, value))
                self._last_dps[str(dps_id)] = value
                self._available = True
                return True
            except Exception as err:
                _LOGGER.error("Value command failed for %s dps %s: %s", self.device_id, dps_id, err)
                self._available = False
                self._tuya = None
                return False
