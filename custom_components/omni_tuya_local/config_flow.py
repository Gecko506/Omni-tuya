from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    CONF_API_KEY,
    CONF_API_SECRET,
    CONF_HOST,
    CONF_REGION,
    DEFAULT_REGION,
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
    """
    Options flow:
      Step 1 – Select device from list (shows current IP)
      Step 2 – Enter / update only the IP address
                (local_key is auto-fetched from Tuya Cloud, no need to enter it here)
    """

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry
        self._selected_device_id: str | None = None
        self._devices: dict[str, dict] = {}

    # ── Step 1: Pick device ───────────────────────────────────────────────────

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Show a dropdown with all registered devices and their current IPs."""
        from .storage import TuyaDeviceStore

        store = TuyaDeviceStore(self.hass)
        await store.async_load()
        self._devices = store.all()

        if not self._devices:
            return self.async_abort(reason="no_devices")

        if user_input is not None:
            self._selected_device_id = user_input["device_id"]
            return await self.async_step_set_ip()

        device_options = {
            dev_id: "{name}  ·  IP actual: {ip}".format(
                name=conf.get("name", dev_id),
                ip=conf.get("host") or conf.get("ip") or "sin IP",
            )
            for dev_id, conf in self._devices.items()
        }

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {vol.Required("device_id"): vol.In(device_options)}
            ),
            description_placeholders={"count": str(len(self._devices))},
        )

    # ── Step 2: Enter IP ──────────────────────────────────────────────────────

    async def async_step_set_ip(self, user_input: dict[str, Any] | None = None):
        """Edit only the IP address for the selected device."""
        from .storage import TuyaDeviceStore

        store = TuyaDeviceStore(self.hass)
        await store.async_load()
        dev = store.get(self._selected_device_id) or {}

        errors: dict[str, str] = {}

        if user_input is not None:
            ip = user_input.get(CONF_HOST, "").strip()

            if ip and not _is_valid_ip(ip):
                errors[CONF_HOST] = "invalid_ip"
            else:
                updated = dict(dev)
                updated[CONF_HOST] = ip
                updated["ip"] = ip          # keep both keys in sync
                await store.add(updated)

                # Reload coordinator so the new IP takes effect immediately
                try:
                    coordinator = self.hass.data[DOMAIN][self._config_entry.entry_id]
                    await coordinator.async_reload_devices()
                except Exception:
                    pass

                return self.async_create_entry(title="", data={})

        current_ip = dev.get("host") or dev.get("ip") or ""

        return self.async_show_form(
            step_id="set_ip",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_HOST, default=current_ip): str,
                }
            ),
            description_placeholders={
                "device_name": dev.get("name", self._selected_device_id or ""),
                "device_id": self._selected_device_id or "",
                "current_ip": current_ip or "sin IP configurada",
            },
            errors=errors,
        )


def _is_valid_ip(ip: str) -> bool:
    """Basic IP address format check."""
    import re
    pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
    if not re.match(pattern, ip):
        return False
    return all(0 <= int(part) <= 255 for part in ip.split("."))
