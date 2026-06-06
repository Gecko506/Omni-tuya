from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import STORAGE_KEY, STORAGE_VERSION
from .models import normalize_device


class TuyaDeviceStore:
    def __init__(self, hass: HomeAssistant) -> None:
        self._store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self._devices: dict[str, dict] = {}
        self.cloud_config: dict = {}

    async def async_load(self) -> None:
        data = await self._store.async_load() or {}
        self._devices = {
            dev_id: normalize_device(config)
            for dev_id, config in (data.get("devices") or {}).items()
            if config.get("device_id") or dev_id
        }
        self.cloud_config = dict(data.get("cloud_config") or {})

    async def async_save(self) -> None:
        await self._store.async_save({
            "devices": self._devices,
            "cloud_config": self.cloud_config,
        })

    def all(self) -> dict[str, dict]:
        return dict(self._devices)

    def get(self, device_id: str) -> dict | None:
        return self._devices.get(device_id)

    async def add(self, config: dict) -> dict:
        normalized = normalize_device(config)
        self._devices[normalized["device_id"]] = normalized
        await self.async_save()
        return normalized

    async def add_many(self, configs: list[dict]) -> list[dict]:
        imported = []
        for config in configs:
            normalized = normalize_device(config)
            if normalized["device_id"]:
                self._devices[normalized["device_id"]] = normalized
                imported.append(normalized)
        await self.async_save()
        return imported

    async def remove(self, device_id: str) -> bool:
        removed = self._devices.pop(device_id, None) is not None
        if removed:
            await self.async_save()
        return removed
