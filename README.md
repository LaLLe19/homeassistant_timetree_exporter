<p align="center">
  <img src="logo.png" width="200" alt="TimeTree Exporter Logo">
</p>

<h1 align="center">Home Assistant TimeTree Exporter</h1>

<p align="center">
  <a href="https://hacs.xyz">
    <img src="https://img.shields.io/badge/HACS-Custom-orange.svg">
  </a>
  <img src="https://img.shields.io/badge/Type-Integration-blue.svg">
  <img src="https://img.shields.io/badge/License-MIT-green.svg">
</p>

---

## Overview

**Home Assistant TimeTree Exporter** is a custom integration that exports one or more **TimeTree calendars** to **ICS files**, which can then be imported into Home Assistant’s calendar system.

---

## Features

- Export **multiple TimeTree calendars per account**
- Automatic refresh (configurable interval)
- One ICS file per calendar
- Status & monitoring sensors

---

## How it works (important)

This integration uses the open-source Python package:

**[`timetree-exporter`](https://pypi.org/project/timetree-exporter/)**

The library:
- logs in to TimeTree using your credentials
- fetches calendar metadata and events
- converts events into the iCalendar (ICS) format

THX @eoleedi

---

## 📦 Installation (HACS – recommended)

1. Open **HACS**
2. Go to **Integrations**
3. Click **⋮ → Custom repositories**
4. Add this repository  -> https://github.com/LaLLe19/timetree_exporter/
   - Type: **Integration**
5. Install **TimeTree Exporter**
6. Restart Home Assistant

---

## Configuration

1. Go to **Settings → Devices & Services**
2. Click **Add Integration**
3. Select **TimeTree Exporter**

### Configuration steps

1. Enter your **TimeTree email and password**
2. Choose a calendarname and select the TimeTree calendar to export 
3. After succesfull export you are free to adjust update interval in instance options.
4. Use *.ics file in Homeassistant (see below)

You can add **multiple instances** of the integration  
(one per TimeTree calendar).

---

## ICS File Location

For each configured calendar, an ICS file is created under:

/config/www/timetree_<calendar_name>.ics

---

## Using the ICS file in Home Assistant

### ICS Calendar integration (recommended)

1. Open **HACS**
2. Install coustum Integration **ICS Calendar** [https://github.com/franc6/ics_calendar]
3. Enter the URL: 
   http://<your-ha-url>/local/timetree_<calendar_name>.ics
4. Enable **auto refresh**

### Other Options

You can use any other ics-calendar integration, import to google calendar ...

## Sensors

Each calendar creates its own set of sensors, for example:

| Sensor                 | Description               |
| ---------------------- | ------------------------- |
| Status                 | idle / ok / error         |
| Last successful export | Timestamp                 |
| Last error             | Error message             |
| Event count            | Number of exported events |
| ICS file size          | File size in kB           |

## License

MIT License

## 🙌 Credits

TimeTree Exporter (Python) - https://github.com/eoleedi/TimeTree-Exporter, ICS Calendar Integration - https://github.com/franc6/ics_calendar and Home Assistant Community
