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
