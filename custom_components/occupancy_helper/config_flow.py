"""Config flow for Occupancy Helper integration."""
from __future__ import annotations

import logging
from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_SENSORS,
    CONF_LOGIC,
    CONF_DELAY_OFF,
    CONF_TIMER_ENTITY,
    CONF_ACTIVE_ICON,
    CONF_IDLE_ICON,
    CONF_DEVICE_CLASS,
    DEFAULT_NAME,
    DEFAULT_LOGIC,
    DEFAULT_DEVICE_CLASS,
    LOGIC_OPTIONS,
    SUPPORTED_DEVICE_CLASSES,
)

_LOGGER = logging.getLogger(__name__)


class OccupancyHelperConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Occupancy Helper."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial setup step."""
        errors: dict[str, str] = {}

        # When the integration is freshly installed (no entries exist yet),
        # automatically create the base integration entry silently without forcing
        # a helper creation dialog.
        if not self._async_current_entries() and user_input is None:
            return self.async_create_entry(
                title="Occupancy Helper",
                data={"is_base": True},
            )

        if user_input is not None:
            name = user_input.get(CONF_NAME, "").strip()
            sensors = user_input.get(CONF_SENSORS, [])

            if not name:
                errors[CONF_NAME] = "empty_name"
            if not sensors:
                errors[CONF_SENSORS] = "empty_sensors"

            if not errors:
                return self.async_create_entry(
                    title=name,
                    data=user_input,
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=DEFAULT_NAME): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
                ),
                vol.Required(CONF_SENSORS): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        multiple=True,
                        domain=["binary_sensor", "sensor", "input_boolean"],
                    )
                ),
                vol.Required(
                    CONF_LOGIC, default=DEFAULT_LOGIC
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[{"value": l, "label": l} for l in LOGIC_OPTIONS],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                        translation_key="logic",
                    )
                ),
                vol.Optional(
                    CONF_DELAY_OFF, default={"minutes": 0, "seconds": 0}
                ): selector.DurationSelector(
                    selector.DurationSelectorConfig(enable_day=False)
                ),
                vol.Optional(CONF_TIMER_ENTITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain=["timer", "input_number"]
                    )
                ),
                vol.Optional(
                    CONF_ACTIVE_ICON,
                    description={"suggested_value": "mdi:motion-sensor"},
                ): selector.IconSelector(),
                vol.Optional(
                    CONF_IDLE_ICON,
                    description={"suggested_value": "mdi:motion-sensor-off"},
                ): selector.IconSelector(),
                vol.Optional(
                    CONF_DEVICE_CLASS, default=DEFAULT_DEVICE_CLASS
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            {"value": dc, "label": dc}
                            for dc in SUPPORTED_DEVICE_CLASSES
                        ],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                        translation_key="device_class",
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        if config_entry.data.get("is_base"):
            return OccupancyHelperBaseOptionsFlow(config_entry)
        return OccupancyHelperOptionsFlow(config_entry)


class OccupancyHelperBaseOptionsFlow(config_entries.OptionsFlow):
    """Handle options for base Occupancy Helper integration."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize base options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage base options."""
        return await self.async_step_base(user_input)

    async def async_step_base(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Show base integration information."""
        if user_input is not None:
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="base",
            data_schema=vol.Schema({}),
        )


class OccupancyHelperOptionsFlow(config_entries.OptionsFlow):
    """Handle options for Occupancy Helper."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        current_data = {**self.config_entry.data, **self.config_entry.options}

        if user_input is not None:
            sensors = user_input.get(CONF_SENSORS, [])

            if not sensors:
                errors[CONF_SENSORS] = "empty_sensors"

            if not errors:
                return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_SENSORS,
                    default=current_data.get(CONF_SENSORS, []),
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        multiple=True,
                        domain=["binary_sensor", "sensor", "input_boolean"],
                    )
                ),
                vol.Required(
                    CONF_LOGIC,
                    default=current_data.get(CONF_LOGIC, DEFAULT_LOGIC),
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[{"value": l, "label": l} for l in LOGIC_OPTIONS],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                        translation_key="logic",
                    )
                ),
                vol.Optional(
                    CONF_DELAY_OFF,
                    default=current_data.get(
                        CONF_DELAY_OFF, {"minutes": 0, "seconds": 0}
                    ),
                ): selector.DurationSelector(
                    selector.DurationSelectorConfig(enable_day=False)
                ),
                vol.Optional(
                    CONF_TIMER_ENTITY,
                    description={
                        "suggested_value": current_data.get(CONF_TIMER_ENTITY, "")
                    },
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain=["timer", "input_number"]
                    )
                ),
                vol.Optional(
                    CONF_ACTIVE_ICON,
                    description={
                        "suggested_value": current_data.get(CONF_ACTIVE_ICON, "")
                    },
                ): selector.IconSelector(),
                vol.Optional(
                    CONF_IDLE_ICON,
                    description={
                        "suggested_value": current_data.get(CONF_IDLE_ICON, "")
                    },
                ): selector.IconSelector(),
                vol.Optional(
                    CONF_DEVICE_CLASS,
                    default=current_data.get(
                        CONF_DEVICE_CLASS, DEFAULT_DEVICE_CLASS
                    ),
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            {"value": dc, "label": dc}
                            for dc in SUPPORTED_DEVICE_CLASSES
                        ],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                        translation_key="device_class",
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            errors=errors,
        )
