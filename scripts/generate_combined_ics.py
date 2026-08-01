#!/usr/bin/env python3
"""
Generate planner_combined.ics from data/all_days.json.
"""

from datetime import date, datetime, time, timedelta
import json
import os
import uuid

DATA_PATH = os.path.join("data", "all_days.json")
OUTPUT_PATH = "planner_combined.ics"

START = date(2026, 8, 2)
END = date(2026, 8, 31)


ROUTINE_SLOTS = [
    ("Breakfast", time(7, 0), 30),
    ("Exercise Bike", time(7, 30), 30),
    ("Shower / Get Ready", time(8, 0), 60),
    ("Study 1", time(9, 0), 90),
    ("Break", time(10, 30), 15),
    ("Study 2", time(10, 45), 90),
    ("Lunch", time(12, 15), 45),
    ("Study 3", time(13, 0), 90),
    ("Break", time(14, 30), 15),
    ("Flashcards / Review", time(14, 45), 60),
]


def dtfmt(dt: datetime) -> str:
    return dt.strftime("%Y%m%dT%H%M%S")


def escape(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace("\n", "\\n")
        .replace(",", "\\,")
        .replace(";", "\\;")
    )


def vevent(uid, dtstamp, dtstart, dtend, summary,
           description="", location=""):
    lines = [
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{dtfmt(dtstamp)}",
        f"DTSTART:{dtfmt(dtstart)}",
        f"DTEND:{dtfmt(dtend)}",
        f"SUMMARY:{escape(summary)}",
    ]

    if description:
        lines.append(f"DESCRIPTION:{escape(description)}")

    if location:
        lines.append(f"LOCATION:{escape(location)}")

    lines.append("END:VEVENT")

    return "\r\n".join(lines)


def load_metadata():
    if not os.path.exists(DATA_PATH):
        print(f"Missing {DATA_PATH}")
        return {}

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    metadata = load_metadata()

    now = datetime.utcnow()

    calendar = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//TEAS Planner//EN",
        "CALSCALE:GREGORIAN",
    ]

    current = START

    event_count = 0

    while current <= END:

        day = current.isoformat()

        info = metadata.get(day, {})

        focus = info.get("focus", "General Study")
        resources = info.get("resources", "")

        for title, start_time, minutes in ROUTINE_SLOTS:

            start = datetime.combine(current, start_time)
            end = start + timedelta(minutes=minutes)

            description = (
                f"Focus: {focus}\n"
                f"Resources: {resources}"
            )

            calendar.append(
                vevent(
                    str(uuid.uuid4()),
                    now,
                    start,
                    end,
                    title,
                    description,
                )
            )

            event_count += 1

        # Hydration reminders
        for reminder in (time(10, 30), time(14, 30)):
            start = datetime.combine(current, reminder)
            end = start + timedelta(minutes=5)

            calendar.append(
                vevent(
                    str(uuid.uuid4()),
                    now,
                    start,
                    end,
                    "Hydrate & Stretch",
                    "Drink water and stretch.",
                )
            )

            event_count += 1

        # Daily checklist
        start = datetime.combine(current, time(16, 30))
        end = start + timedelta(minutes=15)

        checklist = "\n".join([
            "☐ Complete lessons",
            "☐ Practice questions",
            "☐ Review mistakes",
            "☐ Flashcards",
            "☐ Hydrate",
        ])

        calendar.append(
            vevent(
                str(uuid.uuid4()),
                now,
                start,
                end,
                "Daily Checklist",
                checklist,
            )
        )

        event_count += 1

        # Doctor appointment
        if day == "2026-08-05":
            start = datetime.combine(current, time(8, 0))
            end = start + timedelta(minutes=30)

            calendar.append(
                vevent(
                    str(uuid.uuid4()),
                    now,
                    start,
                    end,
                    "Doctor Appointment",
                    "Doctor appointment",
                    "Clinic",
                )
            )

            event_count += 1

        # Therapy Fridays
        if current.weekday() == 4 and current.day in (7, 14, 21, 28):
            start = datetime.combine(current, time(13, 30))
            end = start + timedelta(hours=1)

            calendar.append(
                vevent(
                    str(uuid.uuid4()),
                    now,
                    start,
                    end,
                    "Therapy Appointment",
                    "Therapy appointment",
                    "Therapist Office",
                )
            )

            event_count += 1

        current += timedelta(days=1)

    calendar.append("END:VCALENDAR")

    with open(OUTPUT_PATH, "w", encoding="utf-8", newline="") as f:
        f.write("\r\n".join(calendar))
        f.write("\r\n")

    print(f"Wrote {OUTPUT_PATH} with {event_count} events")


if __name__ == "__main__":
    main()
