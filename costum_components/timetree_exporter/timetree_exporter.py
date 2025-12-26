from datetime import datetime
from icalendar import Calendar
from importlib.metadata import version

from timetree_exporter import TimeTreeEvent, ICalEventFormatter
from timetree_exporter.api.auth import login
from timetree_exporter.api.calendar import TimeTreeCalendar



def run_export(
    email: str,
    password: str,
    calendar_code: str,
    output_path: str,
    hass_data: dict,
):
    """Perform the TimeTree → ICS export."""

    try:
        # 1️⃣ Login
        session_id = login(email, password)

        # 2️⃣ Kalender abrufen
        calendar = TimeTreeCalendar(session_id)
        metadatas = calendar.get_metadata()
        metadatas = [m for m in metadatas if m["deactivated_at"] is None]

        if not metadatas:
            raise ValueError("No active calendars found")

        # Kalender auswählen
        metadata = next(
            (m for m in metadatas if m["alias_code"] == calendar_code),
            metadatas[0],
        )

        calendar_id = metadata["id"]
        calendar_name = metadata["name"]

        # 3️⃣ Events laden
        events = calendar.get_events(calendar_id, calendar_name)

        # 4️⃣ ICS erstellen
        cal = Calendar()
        cal.add("prodid", f"-//TimeTree Exporter {version('timetree_exporter')}//EN")
        cal.add("version", "2.0")

        event_count = 0

        for e in events:
            tte = TimeTreeEvent.from_dict(e)
            formatter = ICalEventFormatter(tte)
            ical_event = formatter.to_ical()
            if not ical_event:
                continue

            cal.add_component(ical_event)
            event_count += 1

        cal.add_missing_timezones()

        # 5️⃣ Datei schreiben
        with open(output_path, "wb") as f:
            f.write(cal.to_ical())

        # 📊 Shared State (Sensoren)
        hass_data["status"] = "ok"
        hass_data["last_success"] = datetime.now().isoformat()
        hass_data["last_error"] = None
        hass_data["event_count"] = event_count

        return True

    except Exception as err:
        hass_data["status"] = "error"
        hass_data["last_error"] = str(err)
        return False
