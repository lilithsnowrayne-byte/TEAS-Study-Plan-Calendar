#!/usr/bin/env python3
"""
generate_ics_prototype.py

Generates studies_prototype.ics for Aug 2-6, 2026 using data/first5_days.json
"""
from datetime import datetime, date, time, timedelta
import json
import uuid

DATA_PATH = "data/first5_days.json"

def dtfmt(dt: datetime) -> str:
    return dt.strftime("%Y%m%dT%H%M%S")

def escape(s: str) -> str:
    return s.replace('\\', '\\\\').replace('\n','\\n').replace(',', '\\,').replace(';','\\;')

def vevent(uid, dtstamp, dtstart, dtend, summary, description=''):
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
    lines.append("END:VEVENT")
    return "\\r\\n".join(lines)

with open(DATA_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)

now = datetime.utcnow()
events = []
for ds, meta in data.items():
    d = date.fromisoformat(ds)
    focus = meta.get('focus','Study')
    lessons = meta.get('lessons', [])
    # Create one study event (09:00-10:30) with lessons in description
    start = datetime.combine(d, time(9,0))
    end = start + timedelta(minutes=90)
    uid = str(uuid.uuid4())
    desc_lines = [f"Focus: {focus}", "Lessons:"]
    for lesson in lessons:
        title = lesson.get('title')
        url = lesson.get('url')
        desc_lines.append(f"- {title} ({url})")
    description = "\\n".join(desc_lines)
    events.append(vevent(uid, now, start, end, f"Study — {focus}", description))

ical = []
ical.extend([
    'BEGIN:VCALENDAR',
    'VERSION:2.0',
    'PRODID:-//TEAS Planner Prototype//EN',
])
ical.extend(events)
ical.append('END:VCALENDAR')

with open('studies_prototype.ics','w',encoding='utf-8') as f:
    f.write('\\r\\n'.join(ical) + '\\r\\n')

print('Wrote studies_prototype.ics with', len(events), 'events')
