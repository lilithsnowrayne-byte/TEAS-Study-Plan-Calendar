#!/usr/bin/env python3
"""
generate_ics.py

Generates 4 .ics files for Aug 2-31, 2026:

- routine.ics         : daily routine events (breakfast, exercise, shower, study blocks, breaks, flashcards)
- studies.ics         : study-session events for each date with Focus, Resources, and Goals in DESCRIPTION
- reminders.ics       : hydration & stretch reminders during breaks and a daily completion checklist event
- appointments.ics    : doctor appointment (Aug 5, 8:00) and therapy appointments (Fridays at 13:30)

No external packages required. Runs on Python 3.6+.
"""

from datetime import date, datetime, time, timedelta
import uuid

# CONFIG: date range
START = date(2026, 8, 2)
END = date(2026, 8, 31)

# Utility functions
def daterange(start_date, end_date):
    d = start_date
    while d <= end_date:
        yield d
        d += timedelta(days=1)

def dtfmt(dt: datetime) -> str:
    # YYYYMMDDTHHMMSS (floating-time - no timezone)
    return dt.strftime("%Y%m%dT%H%M%S")

def escape_ics_text(s: str) -> str:
    # Escape newline, comma, semicolon, backslash per RFC5545
    return s.replace("\\", "\\\\").replace("\n", "\\n").replace(",", "\\,").replace(";", "\\;")

def vevent(uid: str, dtstamp: datetime, dtstart: datetime, dtend: datetime, summary: str, description: str = "", location: str = "") -> str:
    lines = [
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{dtfmt(dtstamp)}",
        f"DTSTART:{dtfmt(dtstart)}",
        f"DTEND:{dtfmt(dtend)}",
        f"SUMMARY:{escape_ics_text(summary)}"
    ]
    if description:
        lines.append(f"DESCRIPTION:{escape_ics_text(description)}")
    if location:
        lines.append(f"LOCATION:{escape_ics_text(location)}")
    lines.append("END:VEVENT")
    return "\r\n".join(lines)

def write_calendar(filename: str, events: list, prodid: str = "-//TEAS Planner//EN") -> None:
    now = datetime.utcnow()
    header = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        f"PRODID:{prodid}",
        f"NAME:{escape_ics_text(filename)}",
        f"X-WR-CALNAME:{escape_ics_text(filename)}",
    ]
    footer = ["END:VCALENDAR"]
    body = []
    for ev in events:
        body.append(ev)
    content = "\r\n".join(header + body + footer) + "\r\n"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Wrote {filename} ({len(events)} events)")

# Build per-day metadata (Focus, Resources, Goals)
# Each entry keyed by date string 'YYYY-MM-DD'
daily_meta = {
    "2026-08-02": {"focus":"Math: Fractions, decimals, percentages","resources":"Khan Academy; Organic Chemistry Tutor; Union Test Prep"},
    "2026-08-03": {"focus":"Math: Algebra & equations","resources":"Khan Academy; Organic Chemistry Tutor; Union Test Prep"},
    "2026-08-04": {"focus":"Reading: Main idea & inference","resources":"Union Test Prep; Quizlet"},
    "2026-08-05": {"focus":"Anatomy (Doctor appointment 8:00)","resources":"OpenStax; Crash Course; Quizlet","appointment":"Doctor 08:00"},
    "2026-08-06": {"focus":"Science: Body systems","resources":"OpenStax; Crash Course; Quizlet"},
    "2026-08-07": {"focus":"English","resources":"","appointment":"Therapy 13:30"},
    "2026-08-08": {"focus":"Weekly practice test","resources":""},
    "2026-08-09": {"focus":"Science: Nervous/Endocrine","resources":"OpenStax; Crash Course; Quizlet"},
    "2026-08-10": {"focus":"Science: Reproductive","resources":"OpenStax; Crash Course; Quizlet"},
    "2026-08-11": {"focus":"Science: Cell biology","resources":"OpenStax; Crash Course; Quizlet"},
    "2026-08-12": {"focus":"Science: Genetics","resources":"OpenStax; Crash Course; Quizlet"},
    "2026-08-13": {"focus":"Science: Chemistry","resources":"OpenStax; Crash Course; Quizlet"},
    "2026-08-14": {"focus":"Chemistry","resources":"","appointment":"Therapy 13:30"},
    "2026-08-15": {"focus":"Scientific reasoning","resources":""},
    "2026-08-16": {"focus":"Reading: Tone","resources":"Union Test Prep; Quizlet"},
    "2026-08-17": {"focus":"Reading: Compare passages","resources":"Union Test Prep; Quizlet"},
    "2026-08-18": {"focus":"English: Grammar","resources":"Quizlet; Union Test Prep"},
    "2026-08-19": {"focus":"English: Punctuation","resources":"Quizlet; Union Test Prep"},
    "2026-08-20": {"focus":"English: Revision","resources":"Quizlet; Union Test Prep"},
    "2026-08-21": {"focus":"Vocabulary","resources":"","appointment":"Therapy 13:30"},
    "2026-08-22": {"focus":"Mixed practice","resources":""},
    "2026-08-23": {"focus":"Practice Exam #1","resources":""},
    "2026-08-24": {"focus":"Weak areas","resources":""},
    "2026-08-25": {"focus":"Math review","resources":""},
    "2026-08-26": {"focus":"Science review","resources":""},
    "2026-08-27": {"focus":"Reading review","resources":""},
    "2026-08-28": {"focus":"Practice Exam #2","resources":"","appointment":"Therapy 13:30"},
    "2026-08-29": {"focus":"Practice Exam #3","resources":""},
    "2026-08-30": {"focus":"Final review","resources":""},
    "2026-08-31": {"focus":"Confidence day","resources":""},
}

# Default goals (same each day)
default_goals = [
    "Complete lessons",
    "30 practice questions",
    "Review mistakes",
    "20 minutes flashcards",
    "Drink water and stretch during breaks"
]

# Routine times (24-hour)
# Breakfast 7:00 (duration 30 min)
# Exercise 7:30 (30 min)
# Shower 8:00 (30 min)
# Study1 9:00-10:30
# Break 10:30-10:45
# Study2 10:45-12:15
# Lunch 12:15-13:00
# Study3 13:00-14:30
# Break 14:30-14:45
# Flashcards 14:45-15:45
routine_slots = [
    ("Breakfast", time(7,0), timedelta(minutes=30)),
    ("Exercise Bike", time(7,30), timedelta(minutes=30)),
    ("Shower / Get Ready", time(8,0), timedelta(minutes=60)),  # 8:00 to 9:00 gives buffer until study
    ("Study 1", time(9,0), timedelta(minutes=90)),
    ("Break (10:30)", time(10,30), timedelta(minutes=15)),
    ("Study 2", time(10,45), timedelta(minutes=90)),
    ("Lunch", time(12,15), timedelta(minutes=45)),
    ("Study 3", time(13,0), timedelta(minutes=90)),
    ("Break (14:30)", time(14,30), timedelta(minutes=15)),
    ("Flashcards / Review", time(14,45), timedelta(minutes=60)),
]

# Build events for each calendar
now = datetime.utcnow()
routine_events = []
study_events = []
reminder_events = []
appointment_events = []

for d in daterange(START, END):
    ds = d.isoformat()
    meta = daily_meta.get(ds, {"focus":"General study","resources":""})
    focus = meta.get("focus","General study")
    resources = meta.get("resources","")
    appointment_note = meta.get("appointment","")

    # Routine events (one per slot)
    for slot_name, slot_start_time, duration in routine_slots:
        start_dt = datetime.combine(d, slot_start_time)
        end_dt = start_dt + duration
        uid = str(uuid.uuid4())
        desc_lines = [
            "Daily routine slot",
            slot_name,
            f"Date: {d.isoformat()}",
            "",
            "Daily checklist available in reminders calendar."
        ]
        description = "\n".join(desc_lines)
        routine_events.append(vevent(uid, now, start_dt, end_dt, slot_name, description))

    # Study events: create events for Study 1, Study 2, Study 3, Flashcards with per-day focus/resources/goals
    study_slots = [
        ("Study 1", time(9,0), timedelta(minutes=90)),
        ("Study 2", time(10,45), timedelta(minutes=90)),
        ("Study 3", time(13,0), timedelta(minutes=90)),
        ("Flashcards / Review", time(14,45), timedelta(minutes=60)),
    ]
    for sname, sstart, sdur in study_slots:
        sdt = datetime.combine(d, sstart)
        edt = sdt + sdur
        uid = str(uuid.uuid4())
        desc = f"Focus: {focus}\nResources: {resources}\n\nGoals:\n" + "\n".join(f"- {g}" for g in default_goals)
        study_events.append(vevent(uid, now, sdt, edt, f"{sname} — {focus}", desc))

    # Hydration/stretch reminders during breaks (10:30 and 14:30)
    for rtime in [time(10,30), time(14,30)]:
        sdt = datetime.combine(d, rtime)
        edt = sdt + timedelta(minutes=5)
        uid = str(uuid.uuid4())
        desc = "Reminder: Drink water and stretch during your break."
        reminder_events.append(vevent(uid, now, sdt, edt, "Hydrate & Stretch", desc))

    # Daily completion checklist event at 16:30 for that day
    checklist_start = datetime.combine(d, time(16,30))
    checklist_end = checklist_start + timedelta(minutes=15)
    uid = str(uuid.uuid4())
    checklist_desc = "Daily Completion Checklist:\\n" + "\\n".join(f"☐ {g}" for g in default_goals)
    # Note: DESCRIPTION will be escaped; we want actual checkbox characters in the text, so include them naturally
    checklist_desc_plain = "Daily Completion Checklist\n" + "\n".join(f"☐ {g}" for g in default_goals)
    reminder_events.append(vevent(uid, now, checklist_start, checklist_end, "Daily completion checklist", checklist_desc_plain))

    # Appointments: Doctor on Aug 5 at 08:00; therapy Fridays at 13:30 (Aug 7,14,21,28)
    if ds == "2026-08-05":
        appt_start = datetime.combine(d, time(8,0))
        appt_end = appt_start + timedelta(minutes=30)
        uid = str(uuid.uuid4())
        desc = "Doctor appointment"
        appointment_events.append(vevent(uid, now, appt_start, appt_end, "Doctor Appointment", desc, "Clinic"))

    # Therapy Fridays (1:30 PM) - check weekday 4 (Monday=0, Sunday=6) -> Friday is 4
    if d.weekday() == 4 and d >= date(2026,8,7) and d <= END:
        # Therapy dates listed: Aug 7, 14, 21, 28
        if d.day in (7,14,21,28):
            appt_start = datetime.combine(d, time(13,30))
            appt_end = appt_start + timedelta(minutes=60)
            uid = str(uuid.uuid4())
            desc = "Therapy appointment"
            appointment_events.append(vevent(uid, now, appt_start, appt_end, "Therapy Appointment", desc, "Therapist Office"))

# Write the four .ics files
write_calendar("routine.ics", routine_events, prodid="-//TEAS Planner Routine//EN")
write_calendar("studies.ics", study_events, prodid="-//TEAS Planner Studies//EN")
write_calendar("reminders.ics", reminder_events, prodid="-//TEAS Planner Reminders//EN")
write_calendar("appointments.ics", appointment_events, prodid="-//TEAS Planner Appointments//EN")

print("All calendars generated: routine.ics, studies.ics, reminders.ics, appointments.ics")
