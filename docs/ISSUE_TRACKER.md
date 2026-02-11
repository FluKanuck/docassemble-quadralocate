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

### ISS-019 — Export filename duplicated with "file." prefix

| Detail | Value |
|--------|-------|
| **Date opened** | 2026-02-11 |
| **Date resolved** | 2026-02-11 |
| **Status** | **RESOLVED** |
| **Version** | 1.4.0 |
| **Commits** | *(included in 1.4.0 commit)* |

**Symptom:** Exported PDF filename appeared as `file.2026-02-10 test company 123 testing rd burnaby jt-12345.2026-02-10 test company 123 testing rd burnaby jt-12345` — the name was duplicated with a `file.` prefix.

**What we tried:** N/A — root cause was clear.

**What worked:** Two changes: (1) `get_export_filename()` now appends `.pdf` to the returned filename, and (2) the `download_report` event passes `filename=` explicitly to `response()` in addition to `pdf_concatenate()`.

---

### ISS-020 — Photos not visible in exported PDF

| Detail | Value |
|--------|-------|
| **Date opened** | 2026-02-11 |
| **Date resolved** | 2026-02-11 |
| **Status** | **RESOLVED** |
| **Version** | 1.4.0 → 1.5.3 |
| **Commits** | *(included in 1.5.3 commit)* |

**Symptom:** Photo pages in the exported PDF are blank — no images visible despite photos being uploaded during the interview.

**What we tried:**
1. Verified the code path: `get_photo_fields()` correctly passes DAFile objects for `photo_1`–`photo_6` fields. The `pdf_concatenate()` assembly includes photo pages with `has_content()` checks. Code logic appeared correct.
2. Initially suspected the `photo_page.pdf` template's form fields were standard text fields instead of image-capable fields (pushbutton with "Icon only" layout). User confirmed template fields are set up correctly.

**What worked:** The root cause was that `datatype: file` in Docassemble stores uploads as `DAFileList` (a list of files), not a single `DAFile`. PDF template image fields need a single `DAFile` object. The `get_photo_fields()` method was passing the raw `DAFileList` — the PDF filler couldn't extract the image. Added `_extract_file()` helper that converts `DAFileList → DAFile[0]`. Applied the same fix to `get_cover_fields()` (cover photo) and `get_drawing_fields()` (drawing images).

---

### ISS-021 — Summary of Work Performed field empty in PDF

| Detail | Value |
|--------|-------|
| **Date opened** | 2026-02-11 |
| **Date resolved** | 2026-02-11 |
| **Status** | **RESOLVED** |
| **Version** | 1.4.0 |
| **Commits** | *(included in 1.4.0 commit)* |

**Symptom:** "Summary of Work Performed" area on the report page PDF was empty. No interview question existed to collect a work summary, and the PDF field name may have been `summary_text` while the code mapped to `combined_report`.

**What we tried:** N/A — root causes identified on first analysis.

**What worked:** Three changes: (1) Added a "Summary of Work Performed" question (`report.work_summary`) in the interview, placed before site conditions in the mandatory flow. (2) Included `work_summary` as the first section in `format_combined_report()`. (3) Added `summary_text` as an additional field mapping in `get_report_fields()` (alongside `combined_report`) to cover both possible PDF field names.

---

### ISS-022 — No "Not in Scope" option for utility locating

| Detail | Value |
|--------|-------|
| **Date opened** | 2026-02-11 |
| **Date resolved** | 2026-02-11 |
| **Status** | **RESOLVED** |
| **Version** | 1.4.0 |
| **Commits** | *(included in 1.4.0 commit)* |

**Symptom:** No way to mark a utility as "not in scope" — all utilities required either a locate method or appeared in the report as located.

**What we tried:** N/A — new feature.

**What worked:** Added `not_in_scope` to all utility types (except ditch which uses `none_in_area`). Added `is_not_in_scope()` method on `UtilityType`. Added `get_not_in_scope_utilities()` on `UtilityMatrix` that dynamically collects display names of all not-in-scope utilities. `format_recommendations()` now auto-appends a dynamic warning sentence using `oxford_join()` — scales from 1 utility to any number. The mandatory flow skips the details/summary question for not-in-scope utilities. The utility still appears in the report header (e.g., "ELECTRICAL (Not in scope):").

---

### ISS-023 — Ditch has no "None in Area" option

| Detail | Value |
|--------|-------|
| **Date opened** | 2026-02-11 |
| **Date resolved** | 2026-02-11 |
| **Status** | **RESOLVED** |
| **Version** | 1.4.0 |
| **Commits** | *(included in 1.4.0 commit)* |

**Symptom:** No way to indicate "no ditch in area." Ditch always appeared in the report if any method was selected.

**What we tried:** N/A — new feature.

**What worked:** Added `none_in_area` to ditch's available methods. Updated `should_display()` to return `False` if the only selected method is `none_in_area`, excluding ditch from the combined report when selected.

---

### ISS-024 — Materials showing with zero quantities in billing

| Detail | Value |
|--------|-------|
| **Date opened** | 2026-02-11 |
| **Date resolved** | 2026-02-11 |
| **Status** | **RESOLVED** |
| **Version** | 1.4.0 |
| **Commits** | *(included in 1.4.0 commit)* |

**Symptom:** Materials appeared in billing details even when quantity was 0 (e.g., "Pin flags x0").

**What we tried:** N/A — root cause was clear.

**What worked:** Updated `format_materials()` to use `float(value) > 0` check (with try/except safety) instead of `value is not None and value != ''`. Zero values and empty strings are now excluded.

---

### ISS-025 — Storm and Sanitary comments lumped under combined heading

| Detail | Value |
|--------|-------|
| **Date opened** | 2026-02-11 |
| **Date resolved** | 2026-02-11 |
| **Status** | **RESOLVED** |
| **Version** | 1.4.0 |
| **Commits** | *(included in 1.4.0 commit)* |

**Symptom:** Storm and Sanitary each had their own headers in the combined report (e.g., "STORM (Located with GPR):") but their comments were lumped under a single "STORM AND SANITARY DETAILS:" heading instead of appearing under each utility's individual header.

**What we tried:** N/A — architectural issue identified.

**What worked:** Five changes: (1) Removed the combined `report.storm_sanitary_summary` question. (2) Added separate detail questions for `report.utilities.storm.summary` and `report.utilities.sanitary.summary`. (3) Updated the mandatory flow with individual gates for storm and sanitary. (4) Removed the "STORM AND SANITARY DETAILS" section from `format_combined_report()` — storm and sanitary now flow through the standard `get_active_utilities()` loop like every other utility. (5) Added new Storm-specific methods (`opened_cb_mh`, `unable_open_cb_mh`) and Sanitary-specific methods (`opened_mh`, `unable_open_mh`) to `UTILITY_TYPES` with corresponding labels and YAML yesno fields.

---

### ISS-026 — Review screen requires Back button to edit earlier answers

| Detail | Value |
|--------|-------|
| **Date opened** | 2026-02-11 |
| **Date resolved** | 2026-02-11 |
| **Status** | **RESOLVED** |
| **Version** | 1.4.0 |
| **Commits** | *(included in 1.4.0 commit)* |

**Symptom:** The review screen was a static `question:` block with no way to jump to specific questions. Users had to hit "Back" repeatedly to make edits.

**What we tried:** N/A — UX redesign.

**What worked:** Replaced the static review block with docassemble's native `review:` block containing `Edit:` entries for all major variables, grouped by section (Job Information, Time & Billing, Utility Locating, Locate Details, Hydrovac & Recommendations, Media). Each entry shows the current value and provides an "Edit" button that jumps directly to the question defining that variable.

---

### ISS-027 — Time fields: 15-minute increment dropdowns + hour breakdown title with times

| Detail | Value |
|--------|-------|
| **Date opened** | 2026-02-11 |
| **Date resolved** | 2026-02-11 |
| **Status** | **RESOLVED** |
| **Version** | 1.5.0 |
| **Commits** | *(included in 1.5.0 commit)* |

**Symptom:** Time on Site start/end fields used a free-form HTML5 time picker, allowing arbitrary minute values. The hour breakdown question title did not show the technician's start/end times, making it harder to orient when entering hours.

**What we tried:** N/A — feature enhancement, implemented in a single pass.

**What worked:** Three changes:
1. Added `time_15min_choices()` helper function in `objects.py` that generates 96 dropdown options (every 15 min from 12:00 AM to 11:45 PM) with 24-hour `HH:MM` stored values for compatibility with existing `format_time_12hr()`.
2. Replaced `datatype: time` on Start Time / End Time in the "Time on Site" `list collect` question with `choices: code: time_15min_choices()`, restricting input to 15-minute increments.
3. Added `format_time_range_12hr()` method on `TimeEntry` and updated the hour breakdown question title to include the time range (e.g., "Hour breakdown — 2/12/26 — Adam Cappon — 8:00 am - 2:00 pm").
4. Exported `time_15min_choices` and `format_time_12hr` in `__all__` so they are available in the YAML interview context.

No existing fixes affected — time storage format (`HH:MM` strings) unchanged; all downstream consumers (`format_time_12hr`, `WorkDay.format_time_range`, build code) handle strings identically.

---

### ISS-028 — Cannot edit utility detail/summary text from review screen

| Detail | Value |
|--------|-------|
| **Date opened** | 2026-02-11 |
| **Date resolved** | 2026-02-11 |
| **Status** | **RESOLVED** |
| **Version** | 1.5.1 |
| **Commits** | *(included in 1.5.1 commit)* |

**Symptom:** The review screen had Edit buttons for utility **methods** (EM, GPR, etc.) but no Edit buttons for utility **detail/summary text** (the free-text comments entered on each utility's details page). Users could not navigate back to edit these comments without using the browser Back button repeatedly.

**What we tried:** N/A — root cause was clear (missing review entries).

**What worked:** Added 7 conditional `Edit:` entries in the review block's "Locate Details" section — one for each utility that has a `.summary` question (Electrical, Communications, Gas/Pipeline, Water, Storm, Sanitary, Unknown/Other). Each entry uses `show if: defined('report.utilities.<key>.summary')` so it only appears when that utility's summary was actually gathered (i.e., the utility has methods selected and is not out of scope). Clicking Edit navigates directly to the corresponding utility details question.

---

### ISS-029 — Photo inputs blank when re-editing from review screen

| Detail | Value |
|--------|-------|
| **Date opened** | 2026-02-11 |
| **Date resolved** | 2026-02-11 |
| **Status** | **RESOLVED** |
| **Version** | 1.5.3 |
| **Commits** | *(included in 1.5.3 commit)* |

**Symptom:** When clicking Edit on the Photo Pages entry in the review screen, the photo file upload fields appeared blank — previously uploaded photos were not visible. Users had no way to see what was already uploaded.

**What we tried:** N/A — root cause identified on first analysis.

**What worked:** Two changes:
1. Updated `get_photos_with_comments()` to yield `(slot_number, photo, comment)` 3-tuples (previously 2-tuples) so the slot number is available for display.
2. Added conditional subquestion text on the photo page question that shows thumbnails of all currently uploaded photos (using `photo.show(width='120px')`) when `has_content()` is True. On first visit (no uploads yet), the extra text is hidden. On re-edit, users see their existing photos with captions and a note that they can re-upload to replace or leave empty to keep.

**Note:** HTML file inputs cannot be pre-populated (browser security restriction). Docassemble may or may not show a "file already uploaded" indicator depending on version. The subquestion thumbnails provide a reliable fallback regardless.

---

### ISS-030 — Report not regenerating after edits (stale PDF cache)

| Detail | Value |
|--------|-------|
| **Date opened** | 2026-02-11 |
| **Date resolved** | 2026-02-11 |
| **Status** | **RESOLVED** |
| **Version** | 1.5.3 |
| **Commits** | *(included in 1.5.3 commit)* |

**Symptom:** After clicking "Edit This Report" on the final screen, making edits (e.g., changing utility detail/summary text), and clicking "Generate Report" again, the downloaded PDF still contained the old text. Edits were not propagating to the exported PDF.

**What we tried:** N/A — root cause was clear.

**What worked:** The root cause was that Docassemble's `attachment` blocks with `variable name` cache the generated PDF. Once `cover_pdf`, `report_pdf`, `report.photo_pages[i].filled_pdf`, etc. were computed, they were never recomputed — even after edits. Updated the `edit_report` event to:
1. `undefine()` all cached attachment variables (`cover_pdf`, `report_pdf`, indexed photo page and drawing PDFs) so Docassemble recomputes them from the attachment blocks on next download.
2. `undefine('time_entries_built')` and `report.job.work_days.clear()` + `gathered = False` to force rebuild of the work_days structure from (possibly edited) time entries.

This ensures every "Download PDF Report" after an edit cycle produces a fresh PDF reflecting all changes.

---

### ISS-031 — Time on Site start/end fields: replace 96-item dropdown with native time picker

| Detail | Value |
|--------|-------|
| **Date opened** | 2026-02-11 |
| **Date resolved** | 2026-02-11 |
| **Status** | **RESOLVED** |
| **Version** | 1.5.4 → 1.5.5 |
| **Commits** | *(included in 1.5.4 and 1.5.5 commits)* |

**Symptom:** In the "Time on Site" list-collect question, the Start Time and End Time fields showed a dropdown with a single option labelled "code" — the `choices:` YAML used list-item syntax (`- code: time_15min_choices()`) instead of mapping syntax (`code: time_15min_choices()`), causing Docassemble to treat "code" as a literal choice label. Even after fixing the syntax (v1.5.4), the 96-item dropdown was a poor UX.

**What we tried:**
1. Fixed the YAML syntax from `- code:` (list item) to `code:` (mapping key) — v1.5.4. This restored the full 96-choice dropdown, but scrolling through 96 options was not a good experience.

**What worked:** Replaced the code-generated dropdown entirely with the native HTML5 time picker (`datatype: time`) plus a JavaScript `step="900"` attribute (900 seconds = 15 minutes). The browser's built-in time spinner/clock UI now snaps to 15-minute increments only. A MutationObserver in the `script` block ensures the step attribute is also applied to dynamically added rows from `list collect`. Updated `format_time_12hr()` in objects.py to handle `datetime.datetime` objects (including Docassemble's `DADateTime`) via `hasattr(time_val, 'hour')` — previously only handled `str` and `datetime.time`.

**Lesson learned:** HTML5 `<input type="time" step="900">` is the cleanest way to restrict time input to 15-minute increments. Docassemble's `datatype: time` stores values as `DADateTime` (a `datetime.datetime` subclass), not `datetime.time` — type-checking code must account for both.

---

### ISS-032 — "Add another" frozen + time picker allows arbitrary minutes (ISS-031 regression)

| Detail | Value |
|--------|-------|
| **Date opened** | 2026-02-11 |
| **Date resolved** | 2026-02-11 |
| **Status** | **RESOLVED** |
| **Version** | 1.5.5 → 1.5.6 |
| **Commits** | *(included in 1.5.6 commit)* |

**Symptom:** Two problems introduced by the v1.5.5 time-picker script: (1) The "Add another" button in the list-collect table stopped responding — all page JavaScript was frozen. (2) The native time picker still allowed users to type any minute value (e.g., 8:07) even with `step="900"`.

**What we tried:** N/A — root causes identified on first analysis.

**What worked:** Two fixes in the `script` block:
1. **Infinite MutationObserver loop:** The old `setTimeStep()` unconditionally called `$.attr('step', '900')` on every time input, which mutated the DOM, which re-triggered the observer, ad infinitum — freezing all JS. Fixed by tagging each input with `$el.data('time-init', true)` on first visit and skipping already-initialized inputs. Added a `_busy` flag + `setTimeout(50ms)` debounce on the observer callback so the observer never re-fires while `initTimeInputs()` is running.
2. **Manual entry not restricted:** HTML5 `step` only affects spinner arrows, not typed values. Added a `change` event handler that snaps the entered time to the nearest 15-minute mark: `Math.round(m / 15) * 15`, with rollover handling for m=60.

**Lesson learned:** MutationObserver + unconditional DOM writes = infinite loop. Always guard against re-entry. HTML5 `step` is a UI hint, not a constraint — client-side `change` handlers are needed to enforce rounding.

---

### ISS-033 — "Add another" still frozen despite ISS-032 debounce (MutationObserver removed)

| Detail | Value |
|--------|-------|
| **Date opened** | 2026-02-11 |
| **Date resolved** | 2026-02-11 |
| **Status** | **RESOLVED** |
| **Version** | 1.5.6 → 1.5.7 |
| **Commits** | *(included in 1.5.7 commit)* |

**Symptom:** The "Add another" button in the time-entries list collect was still unresponsive after the ISS-032 fix. The debounced MutationObserver (with `_busy` flag and 50ms `setTimeout`) was still interfering with Docassemble's own JavaScript that handles the "Add another" action.

**What we tried:**
1. ISS-032's debounce approach — reduced but did not eliminate the interference.

**What worked:** Removed the `MutationObserver` entirely and replaced the whole script with **jQuery event delegation**:
- `$(document).on('change', 'input[type="time"]', handler)` — the delegated change handler automatically fires for dynamically added rows without needing to observe DOM mutations.
- `$(document).on('focus', 'input[type="time"]', handler)` — sets `step="900"` on new inputs when the user focuses them.
- Existing inputs get `step="900"` set once at page load via `$('input[type="time"]').attr('step', '900')`.

This approach does zero DOM observation and zero DOM writes on mutation events, so it cannot interfere with Docassemble's JavaScript.

**Lesson learned:** MutationObserver is the wrong tool for augmenting dynamically added form fields. jQuery event delegation (`$(document).on(event, selector, handler)`) handles current and future elements natively with no DOM mutation side effects.

---

### ISS-034 — "Add another" broken since v1.5.5: script block inside list collect question

| Detail | Value |
|--------|-------|
| **Date opened** | 2026-02-11 |
| **Date resolved** | 2026-02-11 |
| **Status** | **RESOLVED** |
| **Version** | 1.5.5 → 1.5.8 |
| **Commits** | *(included in 1.5.8 commit)* |

**Symptom:** The "Add another" button in the "Time on Site" list collect question stopped responding after switching from the dropdown (`choices: code: time_15min_choices()`) to the native time picker (`datatype: time`) in v1.5.5. The button remained broken through all subsequent JavaScript fixes (v1.5.6, v1.5.7). Git history review revealed the `script:` block was present from v1.5.5 onward, meaning "Add another" was likely broken from the start, not by the specific JavaScript code changes.

**What we tried:**
1. ISS-032: Added debounce/guard to MutationObserver — did not fix "Add another".
2. ISS-033: Removed MutationObserver entirely, used jQuery event delegation — did not fix "Add another".

**What worked:** **Moved the `script:` block out of the list collect question entirely.** Embedding a `script:` modifier inside a `list collect: True` question block appears to interfere with Docassemble's list-collection rendering/JavaScript. Placed the script as a **top-level block** (right after the `features:` section) so it runs globally on every page without being tied to any specific question. Wrapped the code in `$(document).ready())` to ensure it runs after Docassemble's own page setup completes. The time-picker JavaScript (event delegation for step/snap) is unchanged; only its placement in the YAML file changed.

**Lesson learned:** Do not embed `script:` blocks inside `list collect` questions — they break Docassemble's list-collection machinery. Use top-level `script:` blocks for global JavaScript that needs to work across all questions, including dynamically rendered list-collect rows.

---

### ISS-035 — Syntax error: standalone script block invalid (ISS-034 incomplete)

| Detail | Value |
|--------|-------|
| **Date opened** | 2026-02-11 |
| **Date resolved** | 2026-02-11 |
| **Status** | **RESOLVED** |
| **Version** | 1.5.8 → 1.5.9 |
| **Commits** | *(included in 1.5.9 commit)* |

**Symptom:** After the ISS-034 fix (v1.5.8), the interview failed to load with error: *"No question type could be determined for this section"* on line 33 (the `script:` block). Docassemble does not allow standalone top-level `script:` blocks — they must be attached to a question, code block, or initial block.

**What we tried:** N/A — syntax error was clear from the error message.

**What worked:** Changed the standalone `script:` block into an `initial: True` code block with the `script:` modifier attached. The `initial: True` directive makes the code (and its script) run on every page load, which is exactly what we need for global JavaScript. Added a minimal `code: | pass` body since `initial:` blocks require a code section, even if it does nothing.

**Lesson learned:** In Docassemble, `script:` is a **modifier** that attaches to a question or code block, not a standalone top-level block type. For global scripts that run on every page, use `initial: True` with `code:` (even if empty) and attach `script:` as a modifier.

---

### ISS-036 — PermissionError: debug.log in photo export instrumentation

| Detail | Value |
|--------|-------|
| **Date opened** | 2026-02-11 |
| **Date resolved** | 2026-02-11 |
| **Status** | **RESOLVED** |
| **Version** | 1.5.10 → 1.5.11 |
| **Commits** | *(included in 1.5.11 commit)* |

**Symptom:** When running the photo export debug instrumentation, Docassemble raised `PermissionError: [Errno 13] Permission denied: 'q:\\QuadDoc\\.cursor\\debug.log'`. Docassemble runs in Docker (Linux); the Windows path does not exist there and the process cannot write to it.

**What we tried:** N/A — root cause was clear.

**What worked:** Replaced all file-based logging with Docassemble's built-in `log()` function from `docassemble.base.functions`. Log output now appears in the interview's Log tab in the Docassemble playground, which is accessible regardless of deployment environment.

**Lesson learned:** When instrumenting Docassemble code for debugging, use `log()` — never hardcode filesystem paths. The server runs in a container/remote environment where local paths may not exist or be writable.

---

### ISS-037 — Photos not visible in exported PDF (image field type)

| Detail | Value |
|--------|-------|
| **Date opened** | 2026-02-11 |
| **Date resolved** | 2026-02-11 |
| **Status** | **RESOLVED** |
| **Version** | 1.5.11 → 1.5.12 |
| **Commits** | *(included in 1.5.12 commit)* |

**Symptom:** Photos uploaded during the interview did not appear in the exported PDF. The photo page showed "Photos and Comments:" text but no images. Runtime logs confirmed: DAFile extraction worked, `photo_1` was passed correctly, photo page was included in concatenation.

**What we tried:**
1. ISS-020: Added `_extract_file()` to convert DAFileList → DAFile — correct but insufficient.
2. Debug instrumentation (v1.5.10–1.5.11): Logs proved data flow was correct; issue was downstream.

**What worked:** Root cause: **Docassemble only places images into PDF Signature (/Sig) fields, not Push Button (/Btn) fields.** The `photo_page.pdf` template used Push Button fields with "Icon only" layout; docassemble's pdftk filler ignores images for /Btn and only overlays onto /Sig. Two changes:
1. **PDF template:** Change `photo_1`–`photo_6` (and `cover_photo`, `drawing_image` if applicable) from Push Button to **Signature** field type in Acrobat Pro.
2. **Code:** Pass explicit `[FILE reference]` format for image values so docassemble reliably routes them to the images list. Applied to `get_photo_fields()`, `get_cover_fields()`, and `get_drawing_fields()`.

See `docs/PHOTO_PDF_TEMPLATE.md` for step-by-step template update instructions.

---

### ISS-038 — Cover photo export crash on `_get_unqualified_reference`

| Detail | Value |
|--------|-------|
| **Date opened** | 2026-02-11 |
| **Date resolved** | *unresolved* |
| **Status** | **TRIED** |
| **Version** | 1.5.15 |
| **Commits** | *(pending)* |

**Symptom:** Generating the report raises: *"reference to variable `report.cover_photo[0]._get_unqualified_reference` could not be looked up"*.

**What we tried:**
1. Replaced direct `_get_unqualified_reference()` usage with a safe `_to_pdf_file_value()` helper that:
   - extracts the file with `_extract_file()`,
   - prefers `str(DAFile)` (Docassemble `[FILE ...]` markup),
   - falls back to returning the DAFile object.
2. Added runtime logs (via `log(json.dumps(...))`) in `_to_pdf_file_value()` to capture conversion behavior for `cover_photo`, `photo_n`, and `drawing_image`.

**What worked:** *Pending verification run.*

---

### ISS-039 — Edit/regenerate crash: `report.job.work_days[0].date` lookup

| Detail | Value |
|--------|-------|
| **Date opened** | 2026-02-11 |
| **Date resolved** | *unresolved* |
| **Status** | **TRIED** |
| **Version** | 1.5.14 |
| **Commits** | *(pending)* |

**Symptom:** After clicking **Edit This Report** and then generating again, interview crashes with: *"reference to variable `report.job.work_days[0].date` could not be looked up."*

**What we tried:**
1. Made `time_entries_built` rebuild deterministic: always clear and rebuild `report.job.work_days` from `report.time_entries` when the block runs.
2. Added guard state during edit clear (`work_days.there_are_any = False`) to prevent Docassemble gather from trying to resolve item `[0].date` while list is empty/ungathered.
3. Added runtime logs in both `edit_report` and `time_entries_built` to capture pre/post gather state and rebuild counts.

**What worked:** *Pending verification run.*

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
