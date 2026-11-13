"""Binary sensor platform for Occupancy Helper."""
from __future__ import annotations

from collections.abc import Callable
import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_NAME,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import (
    async_call_later,
    async_track_state_change_event,
)

from .const import (
    ATTR_ACTIVE_SENSORS,
    ATTR_DELAY_OFF,
    ATTR_DELAY_OFF_ACTIVE,
    ATTR_LAST_TRIGGER_SENSOR,
    ATTR_LOGIC,
    ATTR_SENSORS,
    ATTR_TIMER_ENTITY,
    CONF_ACTIVE_ICON,
    CONF_DELAY_OFF,
    CONF_DEVICE_CLASS,
    CONF_IDLE_ICON,
    CONF_LOGIC,
    CONF_SENSORS,
    CONF_TIMER_ENTITY,
    DEFAULT_DEVICE_CLASS,
    DEFAULT_LOGIC,
    DEFAULT_NAME,
    LOGIC_AND,
    LOGIC_OR,
)

_LOGGER = logging.getLogger(__name__)

ACTIVE_STATES = {
    "on",
    "true",
    "home",
    "occupied",
    "active",
    "detected",
    "open",
    "motion",
    "1",
}


def parse_delay_seconds(delay: Any) -> float:
    """Parse delay configuration to total seconds."""
    if isinstance(delay, dict):
        return (
            float(delay.get("hours", 0)) * 3600
            + float(delay.get("minutes", 0)) * 60
            + float(delay.get("seconds", 0))
            + float(delay.get("milliseconds", 0)) / 1000
        )
    if isinstance(delay, (int, float)):
        return max(0.0, float(delay))
    if isinstance(delay, str):
        try:
            return max(0.0, float(delay))
        except ValueError:
            parts = delay.split(":")
            try:
                if len(parts) == 3:
                    return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
                if len(parts) == 2:
                    return float(parts[0]) * 60 + float(parts[1])
            except ValueError:
                return 0.0
    return 0.0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Occupancy binary sensor from config entry."""
    if entry.data.get("is_base"):
        return
    async_add_entities([OccupancyBinarySensor(entry)], True)


class OccupancyBinarySensor(BinarySensorEntity):
    """Representation of an Occupancy Binary Sensor Helper."""

    _attr_should_poll = False
    _attr_has_entity_name = True

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        self._entry = entry
        config = {**entry.data, **entry.options}

        self._attr_name = config.get(CONF_NAME, DEFAULT_NAME)
        self._attr_unique_id = f"{entry.entry_id}_occupancy"

        self._sensors: list[str] = config.get(CONF_SENSORS, [])
        self._logic: str = config.get(CONF_LOGIC, DEFAULT_LOGIC)
        self._delay_off_config = config.get(CONF_DELAY_OFF, {"minutes": 0, "seconds": 0})
        self._delay_seconds = parse_delay_seconds(self._delay_off_config)
        self._timer_entity: str | None = config.get(CONF_TIMER_ENTITY) or None

        self._active_icon: str | None = config.get(CONF_ACTIVE_ICON) or None
        self._idle_icon: str | None = config.get(CONF_IDLE_ICON) or None

        device_class = config.get(CONF_DEVICE_CLASS, DEFAULT_DEVICE_CLASS)
        try:
            self._attr_device_class = BinarySensorDeviceClass(device_class)
        except ValueError:
            self._attr_device_class = BinarySensorDeviceClass.OCCUPANCY

        self._active_sensors: list[str] = []
        self._last_trigger_sensor: str | None = None
        self._delay_off_active: bool = False
        self._unsub_delay: Callable[[], None] | None = None

        self._attr_is_on: bool | None = None
        self._attr_available: bool = True

    @property
    def icon(self) -> str | None:
        """Return the dynamic active or idle icon."""
        if self.is_on and self._active_icon:
            return self._active_icon
        if not self.is_on and self._idle_icon:
            return self._idle_icon
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        return {
            ATTR_SENSORS: self._sensors,
            ATTR_ACTIVE_SENSORS: self._active_sensors,
            ATTR_LOGIC: self._logic,
            ATTR_DELAY_OFF: self._get_effective_delay_seconds(),
            ATTR_DELAY_OFF_ACTIVE: self._delay_off_active,
            ATTR_TIMER_ENTITY: self._timer_entity,
            ATTR_LAST_TRIGGER_SENSOR: self._last_trigger_sensor,
        }

    async def async_added_to_hass(self) -> None:
        """Register state listeners when added to hass."""
        tracked_entities = list(self._sensors)
        if self._timer_entity and self._timer_entity not in tracked_entities:
            tracked_entities.append(self._timer_entity)

        if tracked_entities:
            self.async_on_remove(
                async_track_state_change_event(
                    self.hass,
                    tracked_entities,
                    self._async_tracked_state_changed,
                )
            )
        self._evaluate_state(initial=True)

    async def async_will_remove_from_hass(self) -> None:
        """Clean up timers when removing entity."""
        self._cancel_internal_delay()

    def _get_effective_delay_seconds(self) -> float:
        """Get delay in seconds, supporting dynamic input_number entities."""
        if self._timer_entity and self._timer_entity.startswith("input_number."):
            state = self.hass.states.get(self._timer_entity)
            if state is not None:
                try:
                    val = float(state.state)
                    unit = state.attributes.get("unit_of_measurement", "").lower()
                    if "min" in unit:
                        return max(0.0, val * 60)
                    if "h" in unit:
                        return max(0.0, val * 3600)
                    return max(0.0, val)
                except (ValueError, TypeError):
                    pass
        return self._delay_seconds

    @callback
    def _cancel_internal_delay(self) -> None:
        """Cancel internal async_call_later timer."""
        if self._unsub_delay is not None:
            self._unsub_delay()
            self._unsub_delay = None

    @callback
    def _async_tracked_state_changed(self, event: Event) -> None:
        """Handle state change of monitored sensors or linked timer entity."""
        entity_id = event.data.get("entity_id")
        new_state = event.data.get("new_state")

        # Case 1: Linked timer entity changed
        if entity_id == self._timer_entity and self._timer_entity:
            if self._timer_entity.startswith("timer."):
                if new_state and new_state.state in ("idle", "paused"):
                    self._evaluate_active_sensors()
                    if not self._is_raw_occupied():
                        self._attr_is_on = False
                        self._delay_off_active = False
                        self.async_write_ha_state()
                elif new_state and new_state.state == "active":
                    self._delay_off_active = True
                    self._attr_is_on = True
                    self.async_write_ha_state()
                return

        # Case 2: Monitored sensor changed
        if entity_id in self._sensors:
            if new_state and new_state.state.strip().lower() in ACTIVE_STATES:
                self._last_trigger_sensor = entity_id

            self._evaluate_state()
            self.async_write_ha_state()

    @callback
    def _async_internal_delay_expired(self, _now: Any) -> None:
        """Handle expiration of internal delay_off timer."""
        self._unsub_delay = None
        self._delay_off_active = False

        self._evaluate_active_sensors()
        if not self._is_raw_occupied():
            self._attr_is_on = False
            self.async_write_ha_state()

    @callback
    def _evaluate_active_sensors(self) -> None:
        """Scan all monitored sensors and identify currently active ones."""
        active: list[str] = []
        known_sensors = 0

        for entity_id in self._sensors:
            state = self.hass.states.get(entity_id)
            if state is not None and state.state not in (
                STATE_UNAVAILABLE,
                STATE_UNKNOWN,
            ):
                known_sensors += 1
                if state.state.strip().lower() in ACTIVE_STATES:
                    active.append(entity_id)

        self._active_sensors = active
        self._attr_available = known_sensors > 0 or not self._sensors

    def _is_raw_occupied(self) -> bool:
        """Check if monitored conditions currently evaluate to occupied."""
        if not self._sensors:
            return False

        if self._logic == LOGIC_AND:
            return len(self._active_sensors) == len(self._sensors)
        return len(self._active_sensors) > 0

    @callback
    def _evaluate_state(self, initial: bool = False) -> None:
        """Evaluate occupancy state with internal timer or external timer entity."""
        self._evaluate_active_sensors()

        if not self._attr_available:
            self._cancel_internal_delay()
            self._delay_off_active = False
            self._attr_is_on = None
            return

        raw_occupied = self._is_raw_occupied()

        if raw_occupied:
            # Active movement / presence detected
            self._cancel_internal_delay()
            self._delay_off_active = False
            self._attr_is_on = True

            # If external timer is active, cancel it so it resets
            if self._timer_entity and self._timer_entity.startswith("timer."):
                timer_state = self.hass.states.get(self._timer_entity)
                if timer_state and timer_state.state == "active":
                    self.hass.async_create_task(
                        self.hass.services.async_call(
                            "timer", "cancel", {"entity_id": self._timer_entity}
                        )
                    )

            if not self._last_trigger_sensor and self._active_sensors:
                self._last_trigger_sensor = self._active_sensors[0]

        else:
            # Sensors clear
            if self._attr_is_on:
                effective_delay = self._get_effective_delay_seconds()

                if self._timer_entity and self._timer_entity.startswith("timer."):
                    if not initial:
                        service_data: dict[str, Any] = {
                            "entity_id": self._timer_entity
                        }
                        if effective_delay > 0:
                            service_data["duration"] = int(effective_delay)

                        self.hass.async_create_task(
                            self.hass.services.async_call(
                                "timer", "start", service_data
                            )
                        )
                        self._delay_off_active = True
                        self._attr_is_on = True
                    else:
                        timer_state = self.hass.states.get(self._timer_entity)
                        if timer_state and timer_state.state == "active":
                            self._delay_off_active = True
                            self._attr_is_on = True
                        else:
                            self._delay_off_active = False
                            self._attr_is_on = False

                elif effective_delay > 0 and not initial:
                    if self._unsub_delay is None:
                        self._delay_off_active = True
                        self._unsub_delay = async_call_later(
                            self.hass,
                            effective_delay,
                            self._async_internal_delay_expired,
                        )
                        self._attr_is_on = True
                else:
                    self._cancel_internal_delay()
                    self._delay_off_active = False
                    self._attr_is_on = False
            else:
                self._cancel_internal_delay()
                self._delay_off_active = False
                self._attr_is_on = False
