from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.helpers import config_validation as cv

from .cloud import async_fetch_cloud_devices
from .const import (
    CONF_API_KEY,
    CONF_API_SECRET,
    CONF_DEVICE_ID,
    CONF_HOST,
    CONF_LOCAL_KEY,
    CONF_REGION,
    CONF_VERSION,
    BUILD_NUMBER,
    DEFAULT_REGION,
    DEFAULT_VERSION,
    DOMAIN,
    INTEGRATION_VERSION,
    PLATFORMS,
    SERVICE_ADD_DEVICE,
    SERVICE_RELOAD_DEVICES,
    SERVICE_REMOVE_DEVICE,
    SERVICE_SCAN_NETWORK,
    SERVICE_SET_DEVICE_IP,
    SERVICE_SYNC_CLOUD,
    SERVICE_DIAGNOSTICS,
)
from .coordinator import OmniTuyaLocalCoordinator
from .discovery import async_scan_network
from .storage import TuyaDeviceStore

_LOGGER = logging.getLogger(__name__)

ADD_DEVICE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_DEVICE_ID): cv.string,
        vol.Required("name"): cv.string,
        vol.Required(CONF_LOCAL_KEY): cv.string,
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_VERSION, default=DEFAULT_VERSION): cv.string,
        vol.Optional("domain", default="switch"): vol.In(["switch", "light", "lock", "sensor", "climate", "cover"]),
        vol.Optional("product_name", default=""): cv.string,
        vol.Optional("dps_map", default={}): dict,
    }
)

REMOVE_DEVICE_SCHEMA = vol.Schema({vol.Required(CONF_DEVICE_ID): cv.string})

SET_DEVICE_IP_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_DEVICE_ID): cv.string,
        vol.Required(CONF_HOST): cv.string,
    }
)

SYNC_CLOUD_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_API_KEY, default=""): cv.string,
        vol.Optional(CONF_API_SECRET, default=""): cv.string,
        vol.Optional(CONF_REGION, default=DEFAULT_REGION): cv.string,
        vol.Optional(CONF_DEVICE_ID, default=""): cv.string,
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    store = TuyaDeviceStore(hass)
    await store.async_load()

    if entry.data:
        store.cloud_config.update({k: v for k, v in entry.data.items() if v})
        await store.async_save()

    if store.cloud_config.get(CONF_API_KEY) and store.cloud_config.get(CONF_API_SECRET) and not store.all():
        try:
            devices = await async_fetch_cloud_devices(
                hass,
                store.cloud_config[CONF_API_KEY],
                store.cloud_config[CONF_API_SECRET],
                store.cloud_config.get(CONF_REGION, DEFAULT_REGION),
                store.cloud_config.get(CONF_DEVICE_ID, ""),
            )
            await store.add_many(devices)
            _LOGGER.info("Imported %s Tuya devices during setup", len(devices))
        except Exception as err:
            _LOGGER.warning("Tuya cloud sync during setup failed: %s", err)

    coordinator = OmniTuyaLocalCoordinator(hass, entry, store)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _async_register_services(hass, entry.entry_id)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator: OmniTuyaLocalCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_shutdown()
    return unload_ok


def _coordinator(hass: HomeAssistant, entry_id: str) -> OmniTuyaLocalCoordinator:
    return hass.data[DOMAIN][entry_id]


def _async_register_services(hass: HomeAssistant, entry_id: str) -> None:
    if hass.services.has_service(DOMAIN, SERVICE_ADD_DEVICE):
        return

    async def add_device(call: ServiceCall) -> None:
        coord = _coordinator(hass, entry_id)
        await coord.async_add_device(dict(call.data))

    async def remove_device(call: ServiceCall) -> None:
        coord = _coordinator(hass, entry_id)
        await coord.async_remove_device(call.data[CONF_DEVICE_ID])

    async def set_device_ip(call: ServiceCall) -> dict[str, Any]:
        coord = _coordinator(hass, entry_id)
        device_id = call.data[CONF_DEVICE_ID]
        host = call.data[CONF_HOST].strip()
        current = coord.store.get(device_id)
        if not current:
            raise ValueError(f"Tuya device {device_id} is not imported")
        updated = dict(current)
        updated[CONF_HOST] = host
        updated["ip"] = host
        stored = await coord.store.add(updated)
        await coord.async_reload_devices()
        return {"device": stored}

    async def scan_network(call: ServiceCall) -> dict[str, Any]:
        coord = _coordinator(hass, entry_id)
        found = await async_scan_network(hass, list(coord.store.all().values()))
        for device in found:
            if device.get("synced") and device.get(CONF_LOCAL_KEY):
                await coord.async_add_device(device)
        return {"found": found}

    async def sync_cloud(call: ServiceCall) -> dict[str, Any]:
        coord = _coordinator(hass, entry_id)
        cloud_config = dict(coord.store.cloud_config)
        cloud_config.update({k: v for k, v in call.data.items() if v})
        if not cloud_config.get(CONF_API_KEY) or not cloud_config.get(CONF_API_SECRET):
            raise ValueError("Tuya API key and API secret are required")
        coord.store.cloud_config.update(cloud_config)
        await coord.store.async_save()
        devices = await async_fetch_cloud_devices(
            hass,
            cloud_config[CONF_API_KEY],
            cloud_config[CONF_API_SECRET],
            cloud_config.get(CONF_REGION, DEFAULT_REGION),
            cloud_config.get(CONF_DEVICE_ID, ""),
        )
        imported = await coord.async_add_devices(devices)
        return {"imported": imported}

    async def reload_devices(call: ServiceCall) -> None:
        coord = _coordinator(hass, entry_id)
        await coord.async_reload_devices()

    async def diagnostics(call: ServiceCall) -> dict[str, Any]:
        coord = _coordinator(hass, entry_id)
        return {
            "version": INTEGRATION_VERSION,
            "build": BUILD_NUMBER,
            "devices": len(coord.store.all()),
        }

    hass.services.async_register(DOMAIN, SERVICE_ADD_DEVICE, add_device, schema=ADD_DEVICE_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_REMOVE_DEVICE, remove_device, schema=REMOVE_DEVICE_SCHEMA)
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_DEVICE_IP,
        set_device_ip,
        schema=SET_DEVICE_IP_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SCAN_NETWORK,
        scan_network,
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SYNC_CLOUD,
        sync_cloud,
        schema=SYNC_CLOUD_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(DOMAIN, SERVICE_RELOAD_DEVICES, reload_devices)
    hass.services.async_register(
        DOMAIN,
        SERVICE_DIAGNOSTICS,
        diagnostics,
        supports_response=SupportsResponse.ONLY,
    )
