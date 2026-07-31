# TEAS Planner Prototype

This directory contains a 5-page LaTeX prototype for the TEAS study planner and a small script to generate a matching .ics file for the first five days (Aug 2-6, 2026).

Files added:
- planner_prototype.tex       — LaTeX source (A4, minimal) for the 5-page prototype
- data/first5_days.json       — JSON with exact lessons/videos for Aug 2-6, 2026
- scripts/generate_ics_prototype.py — script that reads the JSON and writes studies_prototype.ics

How to build the PDF (requires a LaTeX engine like pdfLaTeX):

1. Install a TeX distribution (TeX Live, MiKTeX, etc.).
2. From the repository root run:
   pdflatex planner_prototype.tex
   pdflatex planner_prototype.tex

The output: planner_prototype.pdf (5 pages, A4)

How to generate the prototype .ics file:

1. Ensure you have Python 3 installed.
2. Run:
   python3 scripts/generate_ics_prototype.py

This will write: studies_prototype.ics

If you'd like, I can compile the PDF here and add the generated planner_prototype.pdf to the repo, or I can switch the PDF pipeline to WeasyPrint/HTML. Let me know which you prefer.
