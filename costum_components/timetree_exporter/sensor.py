import os

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from .const import SIGNAL_TIMETREE_UPDATED  

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up TimeTree sensors for a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    state = data["state"]
    output = data.get("output")

    sensors = [
        TimeTreeStatusSensor(entry, state),
        TimeTreeLastSuccessSensor(entry, state),
        TimeTreeLastErrorSensor(entry, state),
        TimeTreeEventCountSensor(entry, state),
        TimeTreeFileSizeSensor(entry, state, output),
    ]

    async_add_entities(sensors)


class TimeTreeBaseSensor(SensorEntity):
    """Base class for all TimeTree sensors."""

    def __init__(self, entry: ConfigEntry, state: dict):
        self._entry = entry
        self._entry_id = entry.entry_id
        self._state = state

        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "TimeTree",
            "model": "Calendar Export",
        }

    async def async_added_to_hass(self):
        """Register dispatcher to update state."""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                f"{SIGNAL_TIMETREE_UPDATED}_{self._entry_id}",
                self._handle_update,
            )
        )

    def _handle_update(self):
        """Handle updated data from exporter."""
        self.async_write_ha_state()


class TimeTreeStatusSensor(TimeTreeBaseSensor):
    """Sensor showing current export status."""

    def __init__(self, entry, state):
        super().__init__(entry, state)
        self._attr_unique_id = f"{entry.entry_id}_status"
        self._attr_name = f"{entry.title} Status"

    @property
    def native_value(self):
        return self._state.get("status")


class TimeTreeLastSuccessSensor(TimeTreeBaseSensor):
    """Sensor showing last successful export timestamp."""

    def __init__(self, entry, state):
        super().__init__(entry, state)
        self._attr_unique_id = f"{entry.entry_id}_last_success"
        self._attr_name = f"{entry.title} Letzter Export"

    @property
    def native_value(self):
        return self._state.get("last_success")


class TimeTreeLastErrorSensor(TimeTreeBaseSensor):
    """Sensor showing last export error."""

    def __init__(self, entry, state):
        super().__init__(entry, state)
        self._attr_unique_id = f"{entry.entry_id}_last_error"
        self._attr_name = f"{entry.title} Letzter Fehler"

    @property
    def native_value(self):
        return self._state.get("last_error")


class TimeTreeEventCountSensor(TimeTreeBaseSensor):
    """Sensor showing number of exported events."""

    def __init__(self, entry, state):
        super().__init__(entry, state)
        self._attr_unique_id = f"{entry.entry_id}_event_count"
        self._attr_name = f"{entry.title} Anzahl Termine"
        self._attr_native_unit_of_measurement = "events"

    @property
    def native_value(self):
        return self._state.get("event_count")


class TimeTreeFileSizeSensor(TimeTreeBaseSensor):
    """Sensor showing ICS file size in kB."""

    def __init__(self, entry, state, output_path: str):
        super().__init__(entry, state)
        self._output_path = output_path
        self._attr_unique_id = f"{entry.entry_id}_file_size"
        self._attr_name = f"{entry.title} ICS Dateigröße"
        self._attr_native_unit_of_measurement = "kB"

    @property
    def native_value(self):
        if not self._output_path or not os.path.exists(self._output_path):
            return None
        return round(os.path.getsize(self._output_path) / 1024, 1)
