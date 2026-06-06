from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    CONF_API_KEY,
    CONF_API_SECRET,
    CONF_HOST,
    CONF_LOCAL_KEY,
    CONF_REGION,
    CONF_VERSION,
    DEFAULT_REGION,
    DEFAULT_VERSION,
    DOMAIN,
)


class OmniTuyaLocalConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title="Omni Tuya Local", data=user_input)

        schema = vol.Schema(
            {
                vol.Optional(CONF_REGION, default=DEFAULT_REGION): str,
                vol.Optional(CONF_API_KEY, default=""): str,
                vol.Optional(CONF_API_SECRET, default=""): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return OmniTuyaLocalOptionsFlow(config_entry)


class OmniTuyaLocalOptionsFlow(config_entries.OptionsFlow):
    """Options flow to edit cloud credentials and per-device settings (IP, local key, version)."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry
        self._selected_device_id: str | None = None
        self._devices: dict[str, dict] = {}

    # ── Step 1: Main menu ────────────────────────────────────────────────────

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Show menu: edit cloud config or pick a device to edit."""
        from .storage import TuyaDeviceStore

        store = TuyaDeviceStore(self.hass)
        await store.async_load()
        self._devices = store.all()

        if user_input is not None:
            choice = user_input.get("action")
            if choice == "cloud":
                return await self.async_step_cloud_config()
            if choice == "device":
                return await self.async_step_select_device()

        actions: dict[str, str] = {
            "cloud": "☁️ Editar credenciales Cloud API",
        }
        if self._devices:
            actions["device"] = f"📱 Editar un dispositivo ({len(self._devices)} registrados)"

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({vol.Required("action"): vol.In(actions)}),
            description_placeholders={"count": str(len(self._devices))},
        )

    # ── Step 2a: Cloud credentials ────────────────────────────────────────────

    async def async_step_cloud_config(self, user_input: dict[str, Any] | None = None):
        """Edit Tuya Cloud API credentials."""
        from .storage import TuyaDeviceStore

        store = TuyaDeviceStore(self.hass)
        await store.async_load()
        current = store.cloud_config

        if user_input is not None:
            store.cloud_config.update({k: v for k, v in user_input.items() if v is not None})
            await store.async_save()
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="cloud_config",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_REGION, default=current.get(CONF_REGION, DEFAULT_REGION)): str,
                    vol.Optional(CONF_API_KEY, default=current.get(CONF_API_KEY, "")): str,
                    vol.Optional(CONF_API_SECRET, default=current.get(CONF_API_SECRET, "")): str,
                }
            ),
        )

    # ── Step 2b: Select which device to edit ─────────────────────────────────

    async def async_step_select_device(self, user_input: dict[str, Any] | None = None):
        """Present a dropdown of all registered devices."""
        if not self._devices:
            return self.async_abort(reason="no_devices")

        if user_input is not None:
            self._selected_device_id = user_input["device_id"]
            return await self.async_step_edit_device()

        device_options = {
            dev_id: "{name} — {host}".format(
                name=conf.get("name", dev_id),
                host=conf.get("host") or conf.get("ip") or "sin IP",
            )
            for dev_id, conf in self._devices.items()
        }

        return self.async_show_form(
            step_id="select_device",
            data_schema=vol.Schema({vol.Required("device_id"): vol.In(device_options)}),
        )

    # ── Step 3: Edit selected device ──────────────────────────────────────────

    async def async_step_edit_device(self, user_input: dict[str, Any] | None = None):
        """Edit IP address (host), local key, and protocol version for a device."""
        from .storage import TuyaDeviceStore

        store = TuyaDeviceStore(self.hass)
        await store.async_load()
        dev = store.get(self._selected_device_id) or {}

        if user_input is not None:
            updated = dict(dev)
            # Normalise: store both 'host' and 'ip' keys for compatibility
            host = user_input.get(CONF_HOST, "").strip()
            updated[CONF_HOST] = host
            updated["ip"] = host
            updated[CONF_LOCAL_KEY] = user_input.get(CONF_LOCAL_KEY, dev.get(CONF_LOCAL_KEY, "")).strip()
            updated[CONF_VERSION] = user_input.get(CONF_VERSION, dev.get(CONF_VERSION, DEFAULT_VERSION)).strip()
            await store.add(updated)

            # Ask the coordinator to reload so the new IP takes effect immediately
            try:
                coordinator = self.hass.data[DOMAIN][self._config_entry.entry_id]
                await coordinator.async_reload_devices()
            except Exception:
                pass

            return self.async_create_entry(title="", data={})

        current_host = dev.get("host") or dev.get("ip") or ""
        current_key = dev.get("local_key", "")
        current_ver = dev.get("version", DEFAULT_VERSION)

        return self.async_show_form(
            step_id="edit_device",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_HOST, default=current_host): str,
                    vol.Optional(CONF_LOCAL_KEY, default=current_key): str,
                    vol.Optional(CONF_VERSION, default=current_ver): str,
                }
            ),
            description_placeholders={
                "device_name": dev.get("name", self._selected_device_id or ""),
                "device_id": self._selected_device_id or "",
            },
        )
