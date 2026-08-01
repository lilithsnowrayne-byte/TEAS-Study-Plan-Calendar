#!/usr/bin/env python3 """ scripts/generate_combined_ics.py

Generates planner_combined.ics for Aug 2-31, 2026 based on data/all_days.json and the routine. """ from datetime import date, datetime, time, timedelta import json import uuid import os

DATA_PATH = os.path.join("data", "all_days.json")

START = date(2026, 8, 2) END = date(2026, 8, 31)

routine_slots = [ ("Breakfast", time(7, 0), timedelta(minutes=30)), ("Exercise Bike", time(7, 30), timedelta(minutes=30)), ("Shower / Get Ready", time(8, 0), timedelta(minutes=60)), ("Study 1", time(9, 0), timedelta(minutes=90)), ("Break (10:30)", time(10, 30), timedelta(minutes=15)), ("Study 2", time(10, 45), timedelta(minutes=90)), ("Lunch", time(12, 15), timedelta(minutes=45)), ("Study 3", time(13, 0), timedelta(minutes=90)), ("Break (14:30)", time(14, 30), timedelta(minutes=15)), ("Flashcards / Review", time(14, 45), timedelta(minutes=60)), ]

def dtfmt(dt: datetime) -> str: return dt.strftime("%Y%m%dT%H%M%S")

def escape(s: str) -> str: return s.replace('\', '\\').replace('\n', '\n').replace(',', '\,').replace(';', '\;')

def vevent(uid, dtstamp, dtstart, dtend, summary, description='', location=''): lines = [ 'BEGIN:VEVENT', f'UID:{uid}', f'DTSTAMP:{dtfmt(dtstamp)}', f'DTSTART:{dtfmt(dtstart)}', f'DTEND:{dtfmt(dtend)}', f'SUMMARY:{escape(summary)}', ] if description: lines.append(f'DESCRIPTION:{escape(description)}') if location: lines.append(f'LOCATION:{escape(location)}') lines.append('END:VEVENT') return "\r\n".join(lines)

if name == 'main': if not os.path.isfile(DATA_PATH): print(f"Data file not found: {DATA_PATH}") else: with open(DATA_PATH, 'r', encoding='utf-8') as f: meta = json.load(f)

    now = datetime.utcnow()
    ical_events = []

    current = START
    while current <= END:
        ds = current.isoformat()
        daymeta = meta.get(ds, {})
        focus = daymeta.get('focus', 'General study')
        resources = daymeta.get('resources', '')

        # Routine events
        for name, start_t, dur in routine_slots:
            sdt = datetime.combine(current, start_t)
            edt = sdt + dur
            uid = str(uuid.uuid4())
            desc = f'Date: {ds}\\n{focus}\\nResources: {resources}'
            ical_events.append(vevent(uid, now, sdt, edt, name, desc))

        # Study events
        study_slots = [
            ("Study 1", time(9, 0), 90),
            ("Study 2", time(10, 45), 90),
            ("Study 3", time(13, 0), 90),
            ("Flashcards / Review", time(14, 45), 60),
        ]
        for sname, sstart, mins in study_slots:
            sdt = datetime.combine(current, sstart)
            edt = sdt + timedelta(minutes=mins)
            uid = str(uuid.uuid4())
            desc = (
                f'Focus: {focus}\\nResources: {resources}\\nGoals:\\n'
                "- Complete lessons\\n"
                "- 30 practice questions\\n"
                "- Review mistakes\\n"
                "- 20 minutes flashcards\\n"
                "- Drink water and stretch during breaks"
            )
            ical_events.append(vevent(uid, now, sdt, edt, f'{sname} — {focus}', desc))

        # Hydration reminders at 10:30 and 14:30
        for r in (time(10, 30), time(14, 30)):
            sdt = datetime.combine(current, r)
            edt = sdt + timedelta(minutes=5)
            uid = str(uuid.uuid4())
            ical_events.append(vevent(uid, now, sdt, edt, 'Hydrate & Stretch', 'Drink water and stretch during your break.'))

        # Daily checklist
        cs = datetime.combine(current, time(16, 30))
        ce = cs + timedelta(minutes=15)
        uid = str(uuid.uuid4())
        checklist = 'Daily Completion Checklist\\n' + '\\n'.join([
            f'☐ {g}' for g in [
                'Complete lessons',
                '30 practice questions',
                'Review mistakes',
                '20 minutes flashcards',
                'Drink water and stretch during breaks',
            ]
        ])
        ical_events.append(vevent(uid, now, cs, ce, 'Daily completion checklist', checklist))

        # Appointments
        if ds == '2026-08-05':
            sdt = datetime.combine(current, time(8, 0))
            edt = sdt + timedelta(minutes=30)
            ical_events.append(vevent(str(uuid.uuid4()), now, sdt, edt, 'Doctor Appointment', 'Doctor appointment', 'Clinic'))

        # Therapy on Fridays (7,14,21,28)
        if current.weekday() == 4 and current.day in (7, 14, 21, 28):
            sdt = datetime.combine(current, time(13, 30))
            edt = sdt + timedelta(minutes=60)
            ical_events.append(vevent(str(uuid.uuid4()), now, sdt, edt, 'Therapy Appointment', 'Therapy appointment', 'Therapist Office'))

        current = current + timedelta(days=1)

    # Build calendar
    ical = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//TEAS Planner Full//EN']
    ical.extend(ical_events)
    ical.append('END:VCALENDAR')

    with open('planner_combined.ics', 'w', encoding='utf-8') as f:
        f.write('\r\n'.join(ical) + '\r\n')

    print('Wrote planner_combined.ics with', len(ical_events), 'events')
