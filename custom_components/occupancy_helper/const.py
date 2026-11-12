"""Constants for the Occupancy Helper integration."""
from __future__ import annotations

DOMAIN = "occupancy_helper"

CONF_SENSORS = "sensors"
CONF_LOGIC = "logic"
CONF_DELAY_OFF = "delay_off"
CONF_TIMER_ENTITY = "timer_entity"
CONF_ACTIVE_ICON = "active_icon"
CONF_IDLE_ICON = "idle_icon"
CONF_DEVICE_CLASS = "device_class"

DEFAULT_NAME = "Occupancy Helper"
DEFAULT_LOGIC = "or"
DEFAULT_DEVICE_CLASS = "occupancy"

LOGIC_OR = "or"
LOGIC_AND = "and"

LOGIC_OPTIONS = [LOGIC_OR, LOGIC_AND]

SUPPORTED_DEVICE_CLASSES = [
    "occupancy",
    "motion",
    "presence",
    "opening",
    "door",
    "window",
]

ATTR_SENSORS = "sensors"
ATTR_ACTIVE_SENSORS = "active_sensors"
ATTR_LOGIC = "logic"
ATTR_DELAY_OFF = "delay_off"
ATTR_DELAY_OFF_ACTIVE = "delay_off_active"
ATTR_TIMER_ENTITY = "timer_entity"
ATTR_LAST_TRIGGER_SENSOR = "last_trigger_sensor"
