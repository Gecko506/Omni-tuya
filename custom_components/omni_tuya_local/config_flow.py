from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries

from .const import CONF_API_KEY, CONF_API_SECRET, CONF_REGION, DEFAULT_REGION, DOMAIN


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
