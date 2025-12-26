from datetime import timedelta

import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import (
    DOMAIN,
    CONF_EMAIL,
    CONF_PASSWORD,
    CONF_CALENDAR_ID,
    CONF_CALENDAR_ENTITY,
    CONF_CALENDAR_NAME,
    CONF_EXPORT_INTERVAL,
    DEFAULT_EXPORT_INTERVAL,
    SIGNAL_TIMETREE_UPDATED,
)
from .timetree_exporter import run_export

_LOGGER = logging.getLogger(__name__)

def _slugify(name: str) -> str:
    return (
        name.strip()
        .lower()
        .replace(" ", "_")
        .replace("/", "_")
    )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up TimeTree Exporter."""

    email = entry.data[CONF_EMAIL]
    password = entry.data[CONF_PASSWORD]
    calendar_id = entry.data[CONF_CALENDAR_ID]
    calendar_entity = entry.options.get(CONF_CALENDAR_ENTITY)
    calendar_name = entry.data[CONF_CALENDAR_NAME]
    slug = _slugify(calendar_name)
   
    export_interval = entry.options.get(
        CONF_EXPORT_INTERVAL, DEFAULT_EXPORT_INTERVAL
    )

    output = f"/config/www/timetree_{slug}.ics"

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "calendar_name": calendar_name,
        "calendar_id": calendar_id,
        "hass_calendar": calendar_entity,
        "Email": email,
        "password": password,
        "output": output,
        "export_interval": export_interval,
        "state": {
            "status": "idle",
            "last_success": None,
            "last_error": None,
            "event_count": None,
        },
    }

    async def _run_export(_=None):
        state = hass.data[DOMAIN][entry.entry_id]["state"]

        _LOGGER.info(
            "TimeTree Export gestartet: %s (%s)",
            entry.title,
            entry.entry_id,
        )
        
        state["status"] = "running"

        ok = await hass.async_add_executor_job(
            run_export,
            email,
            password,
            calendar_id,
            output,
            state,
        )

        if ok:
            state["status"] = "ok"
            
            async_dispatcher_send(
                hass,
                f"{SIGNAL_TIMETREE_UPDATED}_{entry.entry_id}",
            )

            calendar_entity = hass.data[DOMAIN][entry.entry_id].get("hass_calendar")
            if calendar_entity:
                await hass.services.async_call(
                    "homeassistant",
                    "update_entity",
                    {"entity_id": calendar_entity},
                    blocking=False,
                )
        else:
            state["status"] = "error"

    remove_listener = async_track_time_interval(
        hass,
        _run_export,
        timedelta(minutes=export_interval),
    )

    hass.data[DOMAIN][entry.entry_id]["remove_listener"] = remove_listener

    await _run_export()

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    data = hass.data[DOMAIN].pop(entry.entry_id, None)

    if data and "remove_listener" in data:
        data["remove_listener"]()

    return True
