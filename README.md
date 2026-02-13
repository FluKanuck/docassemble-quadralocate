# docassemble.quadralocate

DocAssemble package for **Quadra Utility Locate Report**: site locate reports for Quadra Utility Locating technicians. Produces PDF reports with job info, time entries, utility matrix, photos, drawings, and client signatures.

## Package structure

```
docassemble-quadralocate/
├── setup.py
├── README.md                    # This file
├── docassemble/
│   └── quadralocate/
│       ├── __init__.py          # Version
│       ├── objects.py           # Python classes (LocateReport, TimeEntry, UtilityType, etc.)
│       └── data/
│           ├── questions/       # Interview YAML
│           │   ├── locate_report.yml
│           │   ├── dashboard.yml
│           │   └── job_map.yml
│           ├── templates/       # Report templates (e.g. locate_report.md)
│           └── static/          # Assets (logo, etc.)
└── docs/
    ├── ISSUE_TRACKER.md         # Canonical issue log — read before bug fixes
    ├── INTERVIEW_FLOW.md        # Interview flow and branches
    └── PHOTO_PDF_TEMPLATE.md    # Photo PDF field requirements (/Sig not /Btn)
```

## Development

- **Git repo:** This folder (`docassemble-quadralocate/`) is the Git root. Run all git commands here.
- **Version:** Bump in three places: `setup.py`, `docassemble/quadralocate/__init__.py`, `docassemble/quadralocate/data/questions/locate_report.yml` (revision_date + Version X.Y.Z line).
- **Bug fixes:** Read `docs/ISSUE_TRACKER.md` first; update it in the same commit. Follow `.cursor/rules/regression-aware-fixes.mdc` and `issue-tracker.mdc` (from workspace root).

## Dependencies

- docassemble
- dropbox (optional)
- geopy

See [workspace README](../README.md) and [CLAUDE.md](../CLAUDE.md) for deployment and project context.
