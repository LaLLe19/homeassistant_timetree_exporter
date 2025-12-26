import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.config_entries import OptionsFlowWithReload

from timetree_exporter.api.auth import login
from timetree_exporter.api.calendar import TimeTreeCalendar

from .const import (
    DOMAIN,
    CONF_EMAIL,
    CONF_PASSWORD,
    CONF_CALENDAR_ID,
    CONF_CALENDAR_NAME,
    CONF_EXPORT_INTERVAL,
    DEFAULT_EXPORT_INTERVAL,
)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate invalid authentication."""


class TimeTreeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for TimeTree Exporter."""

    VERSION = 2

    def __init__(self):
        self._email = None
        self._password = None
        self._calendars = {}

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            self._email = user_input[CONF_EMAIL]
            self._password = user_input[CONF_PASSWORD]

            try:
                await self.hass.async_add_executor_job(self._fetch_calendars)
                return await self.async_step_calendar()
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except CannotConnect:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_EMAIL): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )

    async def async_step_calendar(self, user_input=None):
        errors = {}

        if user_input is not None:
            return self.async_create_entry(
                title=f"TimeTree – {user_input[CONF_CALENDAR_NAME]}",
                data={
                    CONF_EMAIL: self._email,
                    CONF_PASSWORD: self._password,
                    CONF_CALENDAR_ID: user_input[CONF_CALENDAR_ID],
                    CONF_CALENDAR_NAME: user_input[CONF_CALENDAR_NAME],
                },
            )

        return self.async_show_form(
            step_id="calendar",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_CALENDAR_NAME): str,
                    vol.Required(CONF_CALENDAR_ID): vol.In(self._calendars),
                }
            ),
            errors=errors,
        )

    def _fetch_calendars(self):
        try:
            session_id = login(self._email, self._password)
        except Exception as err:
            raise InvalidAuth from err

        try:
            calendar = TimeTreeCalendar(session_id)
            metadatas = calendar.get_metadata()
        except Exception as err:
            raise CannotConnect from err

        self._calendars = {
            m["alias_code"]: m["name"]
            for m in metadatas
            if m.get("deactivated_at") is None
        }

        if not self._calendars:
            raise CannotConnect

    async def async_step_import(self, user_input):
        calendar_id = user_input.get(CONF_CALENDAR_ID)

        for entry in self._async_current_entries():
            if entry.data.get(CONF_CALENDAR_ID) == calendar_id:
                return self.async_abort(reason="already_configured")

        return self.async_create_entry(
            title=f"TimeTree – {user_input.get(CONF_CALENDAR_NAME, 'Kalender')}",
            data=user_input,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return TimeTreeOptionsFlow()


class TimeTreeOptionsFlow(OptionsFlowWithReload):
    """Options flow for TimeTree Exporter."""

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_EXPORT_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_EXPORT_INTERVAL,
                            DEFAULT_EXPORT_INTERVAL,
                        ),
                    ): int,
                    vol.Optional(CONF_PASSWORD): str,
                }
            ),
        )
