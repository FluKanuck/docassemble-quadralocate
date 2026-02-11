# Quadra Locate Report — Issue Tracker

> **Purpose:** Living log of every issue encountered, what was tried, and what ultimately resolved it.  
> **Format:** Entries are ordered chronologically (oldest first). Each entry has a status badge.  
> **Maintained by:** The Cursor AI agent updates this file automatically whenever an issue is investigated, a fix is attempted, or a resolution is confirmed.

---

## Status key

| Badge | Meaning |
|-------|---------|
| **RESOLVED** | Fix confirmed working |
| **TRIED** | Attempted but did not fully resolve the issue |
| **OPEN** | Still under investigation |

---

## Issue Log

---

### ISS-001 — `show if` syntax error on conditional fields

| Detail | Value |
|--------|-------|
| **Date opened** | 2026-02-06 |
| **Date resolved** | 2026-02-06 |
| **Status** | **RESOLVED** |
| **Version** | pre-1.0 |
| **Commits** | `0241d06`, `dfd7a0d` |

**Symptom:** Fields that should only appear conditionally (e.g., BC 1 Call Number when provider is not "None") caused YAML errors or did not display correctly.

**What we tried:**
1. Used a `code` block with `show if` to evaluate a not-equal condition (`0241d06`). This partially worked but still caused problems with more complex conditional visibility.

**What worked:** Switched to `js show if` for client-side field visibility, which avoids server round-trips and the YAML parsing issues with code-based `show if` (`dfd7a0d`).

---

### ISS-002 — Signature field name collision / weather question missing for multi-day

| Detail | Value |
|--------|-------|
| **Date opened** | 2026-02-06 |
| **Date resolved** | 2026-02-06 |
| **Status** | **RESOLVED** |
| **Version** | pre-1.0 |
| **Commits** | `327523f` |

**Symptom:** Signature field had a naming conflict; weather question did not appear for multi-day reports; some optional fields crashed the template when left blank.

**What we tried:** N/A — identified root causes on first pass.

**What worked:** Renamed the signature field to avoid collision, ensured the weather question is shown for multi-day reports, and made optional fields in the Jinja template use `| default('')` filters (`327523f`).

---

### ISS-003 — DAList gathering / `list collect` not working for technicians

| Detail | Value |
|--------|-------|
| **Date opened** | 2026-02-06 |
| **Date resolved** | 2026-02-06 |
| **Status** | **RESOLVED** |
| **Version** | pre-1.0 → 1.1.2 |
| **Commits** | `42ff34a`, `5ae0e6a`, `2f1e348`, `532d5b7`, `fda2129`, `c531444`, `01238e4` |

**Symptom:** Technician lists would not gather properly — either the interview looped infinitely, skipped the gathering step, or raised `there_is_another` lookup errors.

**What we tried:**
1. Specified explicit list variables for `list collect` (`42ff34a`) — did not resolve.
2. Removed `if:` conditions from questions to let the mandatory block control flow (`5ae0e6a`) — partial fix.
3. Used `list collect: True` instead of a variable name (`2f1e348`) — did not resolve fully.
4. Switched to traditional `there_is_another` question pattern (`532d5b7`) — closer but still had issues with complex objects.
5. Added `complete_attribute` to DAList configurations (`fda2129`) — necessary but not sufficient alone.
6. Used generic object modifier `[i]` for technician questions (`c531444`) — better but still had edge cases.

**What worked:** Used `list collect` with `minimum_number` to ensure at least one technician is gathered before the loop logic kicks in (`01238e4`, v1.1.2). Combined with the `complete_attribute` and generic object patterns from earlier attempts.

---

### ISS-004 — Template path not found for `pdf_concatenate`

| Detail | Value |
|--------|-------|
| **Date opened** | 2026-02-06 |
| **Date resolved** | 2026-02-06 |
| **Status** | **RESOLVED** |
| **Version** | pre-1.0 |
| **Commits** | `afbd69c` |

**Symptom:** The PDF generation step failed with a file-not-found error when trying to concatenate the report template.

**What we tried:** N/A — root cause was clear.

**What worked:** Used the full package-qualified path (`docassemble.quadralocate:data/templates/locate_report.md`) instead of a bare filename for `pdf_concatenate` (`afbd69c`).

---

### ISS-005 — `.gathered` vs `.gather()` — list never marked as complete

| Detail | Value |
|--------|-------|
| **Date opened** | 2026-02-09 |
| **Date resolved** | 2026-02-09 |
| **Status** | **RESOLVED** |
| **Version** | 1.1.2 → 1.1.3 |
| **Commits** | `c6cac18` |

**Symptom:** Lists appeared to gather all items but the interview kept looping back, never advancing past the gathering step.

**What we tried:** N/A — identified on first analysis.

**What worked:** Replaced `.gathered` (a passive attribute check) with `.gather()` (an active method call that triggers the gathering machinery and sets the flag). Also added Git credential setup and `.gitignore` for credentials in this commit (`c6cac18`).

---

### ISS-006 — `hours.there_are_any` lookup error on DADict

| Detail | Value |
|--------|-------|
| **Date opened** | 2026-02-09 |
| **Date resolved** | 2026-02-09 (after many iterations) |
| **Status** | **RESOLVED** |
| **Version** | 1.1.3 → 1.1.11 |
| **Commits** | `cad4925`, `83eb04d`, `7322a45`, `6d5a2e0`, `893579f`, `e1908f4` |

**Symptom:** Docassemble raised a lookup error for `hours.there_are_any` on the DADict that stores hour breakdowns per technician per day. The variable name was being mangled into an internal intrinsic name (`rgekpcZRCyeu`-style), making it impossible for docassemble to locate the definition.

**What we tried:**
1. Set `hours.there_are_any` directly on the DADict after construction (`cad4925`, v1.1.3) — still failed for indexed access.
2. Set `tech.hours.there_are_any` in the build block (`83eb04d`, v1.1.7) — worked for first technician but not subsequent ones.
3. Set `hours.there_are_any` by index so docassemble finds the variable for all work days (`7322a45`, v1.1.8) — partially resolved but broke on edge cases.
4. Set `hours.there_are_any` in `Technician.init()` so the lookup always succeeds (`6d5a2e0`, v1.1.9) — still hit the intrinsic name problem.
5. Created a custom `HoursDict` class that pre-sets `there_are_any = True` on construction (`893579f`, v1.1.10) — better but required more wiring.

**What worked:** Set `work_days.gathered` and `technicians.gathered` early, pre-built `HoursDict` for every technician, and added a generic `[i][j]` code block that explicitly sets `there_are_any = True` for every combination of time entry index and technician index (`e1908f4`, v1.1.11). This ensures docassemble never needs to search for the variable — it's already defined.

---

### ISS-007 — `single_day_technicians.there_is_another` lookup / infinite loop on single-day

| Detail | Value |
|--------|-------|
| **Date opened** | 2026-02-09 |
| **Date resolved** | 2026-02-09 |
| **Status** | **RESOLVED** |
| **Version** | 1.1.4 → 1.1.5 |
| **Commits** | `62864f7`, `39513f1` |

**Symptom:** On single-day reports, the technician list for single-day mode raised a `there_is_another` lookup error, and the "Time on Site" question appeared twice, causing an infinite loop.

**What we tried:**
1. Fixed `single_day_technicians.there_is_another` lookup (`62864f7`, v1.1.4) — resolved the error but the duplicate Time on Site question still looped.

**What worked:** Removed the duplicate Time on Site question for single-day mode and guarded the loop to prevent re-entry (`39513f1`, v1.1.5).

---

### ISS-008 — Time entries flow: first entry not requested before `gather()`

| Detail | Value |
|--------|-------|
| **Date opened** | 2026-02-09 |
| **Date resolved** | 2026-02-09 |
| **Status** | **RESOLVED** |
| **Version** | 1.1.6 |
| **Commits** | `e8007dc` |

**Symptom:** After the two-table time/billing refactor (v1.1.6, `d3b3e53`), the interview tried to call `gather()` on time entries before the user entered the first entry. The "Any more?" prompt also appeared before any entries existed.

**What we tried:** N/A — clear root cause.

**What worked:** Explicitly requested the first time entry before calling `gather()`, and added a `show if` guard so the "Any more time entries?" question only appears when `len >= 1` (`e8007dc`).

---

### ISS-009 — `rgekpcZRCyeu.methods['em']` — intrinsic name lookup for utilities

| Detail | Value |
|--------|-------|
| **Date opened** | 2026-02-09 |
| **Date resolved** | 2026-02-09 |
| **Status** | **RESOLVED** |
| **Version** | 1.1.12 |
| **Commits** | `6f3c018`, `a607ac3` |

**Symptom:** After the `hours.there_are_any` fix, a new intrinsic-name error appeared: docassemble could not find `rgekpcZRCyeu.methods['em']` — the utilities object was being referenced by an internal name instead of `report.utilities`.

**What we tried:**
1. Declared `utilities` in YAML so docassemble can resolve the intrinsic name to `report.utilities` (`6f3c018`, v1.1.12) — fixed the name resolution but caused an infinite loop.

**What worked:** Moved the utilities initialization into a code block that runs *after* `report.utilities` exists, breaking the circular dependency (`a607ac3`).

---

### ISS-010 — "Input not processed" after weather question

| Detail | Value |
|--------|-------|
| **Date opened** | 2026-02-09 |
| **Date resolved** | 2026-02-10 |
| **Status** | **RESOLVED** |
| **Version** | 1.1.13 |
| **Commits** | `721d0ce`, `6204685` |

**Symptom:** After submitting the weather conditions screen, docassemble displayed "Input not processed" — meaning the submitted form data didn't match any expected variable. The hour breakdown table (Table 2) also didn't render because `TimeEntry.hours.there_are_any` was never set.

**What we tried:**
1. Set `TimeEntry.hours.there_are_any = True` and adjusted the input processing flow (`721d0ce`) — partially fixed but the "input not processed" error persisted for weather specifically.

**What worked:** Fixed the field ordering so that the weather question's variable is processed in the correct mandatory block position. Ensured the weather field is gathered at the right point in the flow (`6204685`, v1.1.13).

---

### ISS-011 — Audit remediation: data loss, config hardening, cleanup

| Detail | Value |
|--------|-------|
| **Date opened** | 2026-02-10 |
| **Date resolved** | 2026-02-10 |
| **Status** | **RESOLVED** |
| **Version** | 1.2.0 |
| **Commits** | `e17efdb` |

**Symptom:** A full audit of the codebase revealed several categories of issues: potential data loss in the review/edit cycle, missing configuration hardening, and accumulated dead code from the many iteration cycles above.

**What we tried:** N/A — comprehensive remediation in a single pass.

**What worked:** Fixed data loss risk in review/edit flow, hardened configuration defaults, cleaned up dead code and debug logging left over from the `hours.there_are_any` debugging marathon (`e17efdb`, v1.2.0).

---

### ISS-012 — `report.time_entries.there_is_another` lookup error after weather screen

| Detail | Value |
|--------|-------|
| **Date opened** | 2026-02-10 |
| **Date resolved** | 2026-02-10 |
| **Status** | **RESOLVED** |
| **Version** | 1.2.1 |
| **Commits** | *(included in 1.2.1 commit)* |

**Symptom:** After answering the Weather Conditions question and clicking Next, the interview crashes with: *"There was a reference to a variable 'report.time_entries.there_is_another' that could not be looked up in the question file."*

**What we tried:**
1. Identified that `report.time_entries` uses `list collect: True` for gathering, which handles `there_is_another` internally during the collection screen. However, when Docassemble re-evaluates the mandatory code block after weather is answered, `gather()` is called again and needs a definition for `there_is_another` that the list-collect mechanism doesn't persist.

**What worked:** Added a `code` block that defines `report.time_entries.there_is_another = False`. With `list collect: True`, all items are added on a single screen, so `there_is_another` should always resolve to `False`. This gives `gather()` a fallback definition on re-evaluation.

---

### ISS-013 — Infinite loop `x.there_are_any` after completing hour breakdowns

| Detail | Value |
|--------|-------|
| **Date opened** | 2026-02-10 |
| **Date resolved** | 2026-02-10 |
| **Status** | **RESOLVED** |
| **Version** | 1.2.2 |
| **Commits** | *(included in 1.2.2 commit)* |

**Symptom:** After completing the hour breakdown for all time entries and clicking Continue, the interview crashes with: *"There appears to be an infinite loop. Variables in stack are x.there_are_any."*

**What we tried:**
1. Traced the circular dependency: mandatory block requests `time_entries_built` → build code creates Technician via `appendObject()` → `Technician.init()` accesses the `hours` DADict before setting `there_are_any` → Docassemble looks up a code block → that block requires `time_entries_built` (which we're already computing) → infinite loop.

**What worked:** Two changes:
1. In `objects.py`, moved `self.hours.there_are_any = True` **before** the for-loop that accesses the DADict in both `TimeEntry.init()` and `Technician.init()`. This prevents the lookup from ever firing during init.
2. In `locate_report.yml`, removed the `time_entries_built` dependency from the fallback code block that defines `report.job.work_days[i].technicians[j].hours.there_are_any`. The block now sets the attribute directly, eliminating the circular dependency.

---

### ISS-014 — `report.time_entries[0].hours.new_item_name` lookup after weather

| Detail | Value |
|--------|-------|
| **Date opened** | 2026-02-10 |
| **Date resolved** | 2026-02-10 |
| **Status** | **RESOLVED** |
| **Version** | 1.2.3 |
| **Commits** | *(included in 1.2.3 commit)* |

**Symptom:** After clicking Next on the weather screen, the interview crashes with: *"There was a reference to a variable 'report.time_entries[0].hours.new_item_name' that could not be looked up."* This appeared after the ISS-013 fix.

**What we tried:**
1. Traced the cause: The hours DADict on TimeEntry has `there_are_any = True` (set in init) but `gathered` was never set. When `gather()` verifies each TimeEntry's completeness, it touches the hours DADict. Docassemble sees "items exist but dict isn't gathered" and enters the DADict gather protocol, asking for `new_item_name` (the next key to add). Since no question defines that variable, it crashes.

**What worked:** Added `self.hours.gathered = True` in both `TimeEntry.init()` and `Technician.init()`, immediately after `there_are_any = True`. This tells Docassemble the dict is pre-populated and complete — no gather protocol needed. The Table 2 hour breakdown question still works because it's driven by `continue button field: hours_entered`, not by the dict's gather protocol; it sets keys directly via `__setitem__`. Previous fixes (ISS-012: `there_is_another`, ISS-013: `there_are_any` order) remain intact.

---

### ISS-015 — `hours.new_item_name` persists despite ISS-014 fix (DADict.__setitem__ resets gathered)

| Detail | Value |
|--------|-------|
| **Date opened** | 2026-02-10 |
| **Date resolved** | 2026-02-10 |
| **Status** | **RESOLVED** |
| **Version** | 1.2.4 |
| **Commits** | *(included in 1.2.4 commit)* |

**Symptom:** Same `report.time_entries[0].hours.new_item_name` error as ISS-014, but occurring earlier — right after client information, before the time entries screen even appears. The ISS-014 fix (`gathered = True` in init) was in place but ineffective.

**What we tried:**
1. Traced the root cause deeper: `DADict.__setitem__` resets `gathered = False` every time a key is assigned. So the init() loop (`self.hours['em'] = 0`, etc.) undoes the `gathered = True` that was set just above it. Moving `gathered = True` after the loop wouldn't help either, because the Table 2 question's field assignments (`hours['em'] = user_value`) would reset it again on the next request cycle. Fighting DADict's gather protocol with attribute flags is a losing battle.

**What worked:** Replaced `DADict` with `HoursDict` (a plain `dict` subclass already in the codebase) for the `hours` attribute in both `TimeEntry.init()` and `Technician.init()`. Plain dicts have no Docassemble gather protocol — no `there_are_any`, `gathered`, or `new_item_name` lookups. The `HoursDict` class carries `there_are_any = True` and `gathered = True` as class-level attributes for belt-and-suspenders safety. A `hasattr` guard prevents overwriting on re-initialization. Previous fixes (ISS-012 `there_is_another`, ISS-013 fallback blocks) remain intact as defense-in-depth.

**Lesson learned:** DADict is the wrong tool for pre-populated, fixed-schema dictionaries. Use a plain dict (HoursDict) whenever the keys are known at creation time and no gather UI is needed.

---

### ISS-016 — `report.job.work_days.there_is_another` lookup after hour breakdowns

| Detail | Value |
|--------|-------|
| **Date opened** | 2026-02-10 |
| **Date resolved** | 2026-02-10 |
| **Status** | **RESOLVED** |
| **Version** | 1.2.5 |
| **Commits** | *(included in 1.2.5 commit)* |

**Symptom:** After completing all hour breakdowns and clicking Next, the interview crashes with: *"There was a reference to a variable 'report.job.work_days.there_is_another' that could not be looked up."*

**What we tried:**
1. Traced the flow: mandatory block reaches `time_entries_built` → build code runs → creates work_days and technicians via `appendObject()` → line 271 calls `len(report.job.work_days)` **before** line 272 sets `gathered = True` → `len()` on an un-gathered DAList triggers the gather protocol → asks `there_is_another` → not defined → crash. Also, `day.technicians.gathered = True` was set **before** the technician append loop (line 252), but `appendObject()` resets `gathered`, leaving technicians un-gathered too.

**What worked:** Three changes:
1. Moved `report.job.work_days.gathered = True` **before** the `len()` call (after all appendObject calls are complete).
2. Moved `day.technicians.gathered = True` to **after** the technician append loop (so it isn't reset by appendObject).
3. Added `there_is_another = False` fallback code blocks for both `report.job.work_days` and `report.job.work_days[i].technicians` — same safety-net pattern that fixed ISS-012 for `time_entries`. This ensures the gather protocol can always complete even if gathered is unexpectedly reset.

All previous fixes (ISS-012 through ISS-015) verified intact.

**Lesson learned:** For manually-built DALists: (a) always set `gathered = True` **after** the last `appendObject()`, and (b) always provide a `there_is_another = False` code block as a safety net.

---

### ISS-017 — Photo page redesign: 6 paired photo/caption slots per page

| Detail | Value |
|--------|-------|
| **Date opened** | 2026-02-10 |
| **Date resolved** | 2026-02-10 |
| **Status** | **RESOLVED** |
| **Version** | 1.2.9 |
| **Commits** | *(see git log)* |

**Symptom:** The old photo upload used a single multi-file upload + single comment per page, preceded by a "how many pages?" count question. The user requested 6 individual photo slots per page, each with its own caption, all optional, with the ability to add more pages, and no export of empty pages.

**What we tried:**
1. Redesigned `PhotoPage` class in `objects.py` to use 6 individual `photo_N`/`comment_N` attributes (N=1..6) with `get_photos_with_comments()` and `has_content()` helpers.
2. Replaced the two YAML questions (count question + per-page upload) with a single 6-slot question using `continue button field` and an `add_another` toggle.
3. Updated the mandatory block to use a manual `while`-loop on `add_another` instead of a count-based `for` loop.
4. Updated `locate_report.md` template to iterate over slots, rendering only uploaded photos with their captions, and skipping empty pages.
5. Updated review screen to show actual photo count instead of `num_photo_pages`.
6. Added `there_is_another = False` safety-net code block for `report.photo_pages` (DAList invariant).

**What worked:** All of the above changes together. The `there_is_another = False` block and `gathered = True` in the mandatory block follow the same safe patterns established in ISS-012/ISS-016.

**Lesson learned:** When replacing a count-based loop with a dynamic `add_another` pattern, the mandatory block must manually walk the list indices and set `gathered = True` after the loop ends, with a `there_is_another = False` safety-net code block.

---

### ISS-018 — PDF export redesign: per-page-type fillable PDF templates with pdf_concatenate

| Detail | Value |
|--------|-------|
| **Date opened** | 2026-02-10 |
| **Date resolved** | 2026-02-10 |
| **Status** | **RESOLVED** |
| **Version** | 1.3.0 |
| **Commits** | *(see git log)* |

**Symptom:** The existing PDF export used a single Markdown template (`locate_report.md`) converted to a plain, unstyled PDF. The output did not match the professionally designed Quadra Locate Sheet (v15 rev7) with its branded headers, structured layouts, and per-page-type formatting.

**What we tried:**
1. Redesigned the entire PDF export pipeline to use fillable PDF templates (one per page type) assembled via `pdf_concatenate()`.
2. Created 5 attachment blocks: `cover_page.pdf`, `report_page.pdf`, `photo_page.pdf`, `drawing_page_letter.pdf`, `drawing_page_wide.pdf`, plus a static `legend_page.pdf`.
3. Added Python field-mapping methods: `get_cover_fields()`, `get_report_fields()`, `get_export_filename()` on `LocateReport`; `get_photo_fields()` on `PhotoPage`; `get_drawing_fields()` on `Drawing`.
4. Added new interview questions: `cover_photo` (optional file upload for cover page) and `missing_docs_other` (free-text "Other" missing docs field).
5. Removed in-interview client signature collection — signature is now a digital signature field left signable on the exported PDF.
6. Updated export filename to `YYYY-MM-DD Client Company Site Address QJN.pdf`.
7. Drawing pages use two templates: `drawing_page_letter.pdf` for normal format and `drawing_page_wide.pdf` for large format (11x17/tabloid), selected per drawing based on `drawing.format`.

**What worked:** All of the above changes together. The old `locate_report.md` is kept for reference but is no longer the primary export. The user must still complete the design-side work: export individual pages from InDesign, add form fields in Acrobat Pro with the exact field names, and place them in `data/templates/` and `data/static/`.

**Lesson learned:** Docassemble's `pdf_concatenate()` with per-page-type `pdf template file` attachments gives full control over page layout while keeping the code modular. Each page type can be designed independently and repeated any number of times.

---

<!-- 
  ┌──────────────────────────────────────────────────────────────────┐
  │  TEMPLATE — Copy this block when adding a new issue.            │
  │  Replace ISS-NNN with the next sequential number.               │
  └──────────────────────────────────────────────────────────────────┘

### ISS-NNN — Short description of the issue

| Detail | Value |
|--------|-------|
| **Date opened** | YYYY-MM-DD |
| **Date resolved** | YYYY-MM-DD or *unresolved* |
| **Status** | **OPEN** / **TRIED** / **RESOLVED** |
| **Version** | X.Y.Z |
| **Commits** | `abcdef0` |

**Symptom:** What the user or developer observed.

**What we tried:**
1. First attempt — result.
2. Second attempt — result.

**What worked:** The final fix and why it resolved the issue.

-->
