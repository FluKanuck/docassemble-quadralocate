# Code Audit Report — AI Slop Patterns

**Project:** QuadDoc (docassemble-quadralocate)  
**Audit date:** 2026-02-13  
**Scope:** All code files (Python, interview YAML, templates) per `.cursorrules` Anti-Slop Rules.

---

## 1. DUPLICATE CODE

| File | Line(s) | Problem | Suggested fix | Priority |
|------|---------|---------|---------------|----------|
| `data/questions/locate_report.yml` | 668–867 | Eight nearly identical utility-method question blocks (Electrical, Communications, Gas, Water, Storm, Sanitary, Ditch, Unknown). Only `report.utilities.<key>` and title text differ; field list is copy-pasted per utility. | Extract one generic block (e.g. `utility_methods_question`) that takes utility key/display name from `report.utilities.UTILITY_TYPES`, or use a YAML include with a single parameterized block. | **High** |
| `data/questions/locate_report.yml` | 868–956 | Eight nearly identical “utility details” blocks (summary field + show if). Same pattern: `report.utilities.<key>.summary` and conditional on `has_any_method()` / `get_missing_doc_labels_for_utility()` / `is_not_in_scope()`. | Single generic block or include driven by utility key from `UTILITY_TYPES`. | **High** |
| `data/questions/locate_report.yml` | 1364–1399 | Ten nearly identical Review “Edit” blocks for `report.drawings[0]` … `report.drawings[9]`. Only index and “Drawing N” label change. | One `review:` entry using `report.drawings[i]` with `i` in range, or a generic template (if Docassemble supports). | **Medium** |
| `data/questions/locate_report.yml` | 57–131 vs 312–384 | Address autocomplete logic duplicated: (1) in `initial: True` script (global delegation), (2) in Job Information question `script:` (findSiteAddressField + bindAutocomplete). Same AJAX, same debounce (350), same dropdown behavior. | Keep a single implementation (e.g. only the initial block’s delegated handler); remove the Job Information–specific duplicate. | **Medium** |
| `data/questions/locate_report.yml` (event `address_suggest`) vs `objects.py` `JobMapService.geocode_address` | 152–163 (YAML) vs 1450–1461 (Python) | Nominatim contact email and User-Agent construction duplicated: same `get_config('nominatim email')` / `get_config('admin email')` / env fallbacks and `get_config('nominatim user agent')` / env / `QuadraLocate/1.0` fallback. | Add a shared helper in `objects.py` (e.g. `get_nominatim_contact_email()`, `get_nominatim_user_agent()`) and call it from both the YAML event code and `JobMapService.geocode_address`. | **Medium** |
| `data/questions/locate_report.yml` | 1412–1432, 1500–1525, 1529–1544 | PDF assembly (cover + report + cont_pages + photo_pages + drawings + legend) implemented three times: in `session_tagged_complete` (archive), `download_report`, and `save_to_dropbox` fallback. Same order and conditions. | Extract one code block or Python helper that returns the list of PDF parts; reuse in all three places. | **High** |
| `data/questions/dashboard.yml` vs `data/questions/job_map.yml` | dashboard 114–139, job_map 206–232 | `interview_list()` plus subtitle parsing (split on `' \| '`) and extraction of job_number, client, address, date duplicated. Job map sync also uses same subtitle format. | Extract shared logic to a Python function in `objects.py` (e.g. `parse_locate_report_subtitle(subtitle)`) and use in both interviews. | **Medium** |

---

## 2. USELESS COMMENTS

| File | Line(s) | Problem | Suggested fix | Priority |
|------|---------|---------|----------------|----------|
| `docassemble/quadralocate/objects.py` | 684–710 | Section comments that only repeat the next line: “# TIME ON SITE”, “# TYPE/TIME”, “# SUPPLEMENTAL”, “# MATERIALS”, “# PROPERTY TYPE”. | Remove these; the method and variable names are self-explanatory. | **Low** |
| `docassemble/quadralocate/objects.py` | 919 | Comment “# Helper functions” — obvious from the following definitions. | Remove. | **Low** |
| `docassemble/quadralocate/objects.py` | 319, 325, 338, 344, 351, 361 | “# Single day format”, “# Multi-day format”, “# Single day - list technicians”, “# Add totals if 2+ technicians”, “# Multi-day - show daily breakdown”, “# Add combined totals” — describe what the next few lines do. | Keep only if they clarify non-obvious branching; otherwise remove. | **Low** |
| `docassemble/quadralocate/objects.py` | 785, 790, 795, 802, 807 | “# Travel Notes”, “# Site Conditions”, “# Utility sections…”, “# Hydrovac recommendation”, “# Recommendations…” — repeat section structure. | Remove; structure is clear from code. | **Low** |

**Keep:** Comments that explain *why* (e.g. DADict/HoursDict, “Do NOT set … so Docassemble shows the question”, ISS references, Nominatim usage policy). No change needed for those.

---

## 3. UNUSED CODE

| File | Line(s) | Problem | Suggested fix | Priority |
|------|---------|---------|---------------|----------|
| `docassemble/quadralocate/objects.py` | 4 | `format_time` is imported from `docassemble.base.util` but never used (only `format_time_12hr` and `format_date` are used). | Remove `format_time` from the import. | **High** |
| `docassemble/quadralocate/objects.py` | 5 | `time` is imported from `datetime` but never used. | Remove `time` from `from datetime import datetime, time`. | **High** |
| `docassemble/quadralocate/objects.py` | 7 | `json` is imported but never used in this module. | Remove `import json`. | **High** |
| `data/questions/locate_report.yml` | 272–298 | Large commented-out block: “Resume Existing Job” and “Edit Submitted Report” questions. Dead code. | Delete the block or move to a separate “future” snippet file; avoid keeping long commented blocks in the main interview. | **Medium** |
| `data/questions/locate_report.yml` | 1796 | Save Progress subquestion says: “You can resume this report at any time by selecting ‘Resume Existing Job’ and entering the job number.” Resume by job number is not implemented (see TODO at 272). | Update copy to match current behavior (e.g. “You can return to this report from the Dashboard” or remove the sentence until resume is implemented). | **Medium** |

---

## 4. MISSING ERROR HANDLING

| File | Line(s) | Problem | Suggested fix | Priority |
|------|---------|---------|---------------|----------|
| `data/questions/locate_report.yml` | 176–183 (event `address_suggest`) | `requests.get()` to Nominatim has `timeout=10` but no try/except. If Nominatim is down or times out, an unhandled exception can propagate. | Wrap the request in try/except; on failure return `response(binaryresponse=b'[]', content_type='application/json')` so the UI degrades gracefully. | **Medium** |
| `data/questions/job_map.yml` | 273–280 (event `serve_archived_pdf`) | If `ReportArchiver.get_archived_path()` returns a path but the file is deleted before `open()`, `open()` can raise. Response only handles “path is None”. | Wrap `open(_pdf_path, 'rb')` in try/except; on IOError/OSError return 404 or 500 with a safe message. | **Low** |
| `docassemble/quadralocate/objects.py` | 457–461, 471–475 | `format_supplemental` / `format_materials` use try/except for float conversion; good. Optional: validate that numeric fields are non-negative where applicable. | Consider adding explicit checks for negative values if they are invalid (e.g. parking, hours). | **Low** |

---

## 5. MAGIC NUMBERS / STRINGS

| File | Line(s) | Problem | Suggested fix | Priority |
|------|---------|---------|---------------|----------|
| `data/questions/locate_report.yml` | 125, 350, 375 | Debounce 350 ms and “900” (step for time inputs) appear inline. Query min length 4 and limit 6 in address_suggest. | Define constants at top of YAML (e.g. in a `code:` block) or in `objects.py` (e.g. `ADDRESS_SUGGEST_DEBOUNCE_MS = 350`, `TIME_INPUT_STEP_SECONDS = 900`, `ADDRESS_SUGGEST_MIN_LEN = 4`, `ADDRESS_SUGGEST_LIMIT = 6`) and reference them. | **Medium** |
| `data/questions/locate_report.yml` | 156, 159 | Fallback string `'admin@quadra.com'` and User-Agent format hardcoded. Same in `objects.py` (1455, 1460). | Single constant or config key (e.g. in objects: `NOMINATIM_DEFAULT_EMAIL = 'admin@quadra.com'`) and reuse. | **Low** |
| `data/questions/locate_report.yml` | 1735 | `_db_folder = '/Quadra Reports'` hardcoded in `save_to_dropbox`. | Move to config or constant (e.g. `DROPBOX_REPORTS_FOLDER` in config / objects). | **Low** |
| `docassemble/quadralocate/objects.py` | 1016 | `min_split = int(max_chars * 0.6)` — 0.6 is a magic ratio. | Define e.g. `MIN_SPLIT_RATIO = 0.6` at module level and use it. | **Low** |
| `data/questions/locate_report.yml` | 1177 | `max: 10` for “Number of drawings”. | Constant e.g. `MAX_DRAWINGS = 10` in objects or YAML and reference. | **Low** |
| `data/templates/locate_report.md` | 106, 135, 137, 159 | “30 days”, “1-604-897-4616” repeated in disclaimer text. | If these values are used elsewhere or may change, consider variables or a single source (e.g. config or template variables). | **Low** |

---

## 6. INCONSISTENT NAMING

| File | Line(s) | Problem | Suggested fix | Priority |
|------|---------|---------|---------------|----------|
| `data/questions/locate_report.yml` | various | Mix of completion flags: `hours_entered`, `page_complete`, `cover_photo_complete`. | Prefer one convention (e.g. all `*_complete` or all `*_entered`) for similar concepts. | **Low** |
| `data/questions/job_map.yml` | 220–232 | Abbreviated names: `_jn`, `_cl`, `_ad`, `_dt`, `_s`, `_synced`, `_skipped`. | Use descriptive names: e.g. `job_number`, `client`, `address`, `date` (or keep single-letter only where scope is tiny and clear). | **Low** |
| `data/questions/dashboard.yml` | 114–139 | Similar use of `parts`, `raw_sessions`; `info` dict keys are clear. | Optional: align variable names with job_map (e.g. `job_number` vs `parts[0]`) for consistency across interviews. | **Low** |

---

## 7. POOR STRUCTURE

| File | Line(s) | Problem | Suggested fix | Priority |
|------|---------|---------|---------------|----------|
| `data/questions/locate_report.yml` | entire file | File is 1,803 lines. .cursorrules allow long main interview YAML but recommend avoiding >500 lines for *new* modules; this file is hard to navigate and edit. | Split into logical includes (e.g. `job_info.yml`, `time_billing.yml`, `utility_matrix.yml`, `utility_details.yml`, `media.yml`, `review_export.yml`) and include them from `locate_report.yml`. Reduces duplication and improves maintainability. | **Medium** |
| `docassemble/quadralocate/objects.py` | 596–598 (get_export_filename) | `import re` is inside the method. | Move `import re` to top of file (with other imports) for consistency and slight performance. | **Low** |
| `docassemble/quadralocate/objects.py` | 929–971 | `format_time_12hr()` is long (~43 lines) with several branches (string parsing, datetime). | Consider splitting: e.g. `_parse_time_string()`, `_format_time_12hr_from_parts(hour, minute)` and a short public `format_time_12hr()`. | **Low** |

---

## Summary by priority

- **High:** 4 (duplicate utility blocks, duplicate utility details, duplicate PDF assembly, unused imports in objects.py).
- **Medium:** 10 (duplicate review drawing blocks, duplicate address autocomplete, duplicate Nominatim config, duplicate PDF assembly in three places, duplicate subtitle parsing, commented-out resume block, outdated Save Progress text, address_suggest error handling, YAML magic numbers, file length / split).
- **Low:** 18 (various comments, serve_archived_pdf error handling, optional validation, remaining magic numbers/strings, naming consistency, import location, format_time_12hr length).

---

## Files audited

- `docassemble/quadralocate/objects.py`
- `docassemble/quadralocate/__init__.py`
- `docassemble/quadralocate/data/questions/locate_report.yml`
- `docassemble/quadralocate/data/questions/job_map.yml`
- `docassemble/quadralocate/data/questions/dashboard.yml`
- `docassemble/quadralocate/data/templates/locate_report.md`

No Python modules under `data/sources` (that directory does not exist; code lives in `objects.py` and `__init__.py`).

---

## Validation Against DocAssemble Documentation

The following checks compare audit suggestions to [DocAssemble documentation](https://docassemble.org/docs) to avoid breaking existing functionality.

### Safe to implement as suggested

| Suggestion | DocAssemble basis |
|------------|-------------------|
| **Remove unused imports** (`format_time`, `time`, `json` in `objects.py`) | Standard Python; no DocAssemble dependency on these names in this package. |
| **Delete or move commented-out resume/edit blocks** (YAML 272–298) | Commented YAML is ignored; removal cannot change behavior. |
| **Update Save Progress subquestion text** (1796) | Copy change only; no variable or flow change. |
| **Wrap `address_suggest` and `serve_archived_pdf` in try/except** | Event code runs in normal Python; exception handling is safe. |
| **Extract Nominatim helpers to `objects.py`** and call from YAML event | `modules:` makes package functions available to all interview code, including event code ([docs: modules](https://docassemble.org/docs/functions)). |
| **Extract PDF parts list to one Python helper** | Code blocks and event code can call module functions; returning a list of PDF parts is safe. |
| **Extract subtitle parsing to `objects.py`** (e.g. `parse_locate_report_subtitle`) | Same as above; call from dashboard and job_map code blocks. |
| **Use constants for `min`/`max`** (e.g. `max: ${ max_drawings }`) | Docs allow [Mako templating for computable validation limits](https://docassemble.org/docs/fields); variable must be defined before the question is needed. |
| **Split interview into includes** | [Include](https://docassemble.org/docs/packages) incorporates YAML “as if part of the current file”; same namespace. Define `report` and `objects` in the main file; included files can reference `report.*`. |
| **Move `import re` to top of `objects.py`** | Standard Python; no DocAssemble impact. |
| **Remove redundant comments** (section headers, “Helper functions”) | No behavioral effect. |

### Implement with DocAssemble-specific care

| Suggestion | Caveat / correct approach |
|------------|---------------------------|
| **Single generic block for utility methods** (Electrical, Communications, …) | Utilities use different method sets (e.g. Ditch: 3 methods; Storm: 8). DocAssemble supports [generic object](https://docassemble.org/docs/fields) with `x` as placeholder. To avoid breaking behavior: use one generic block for type `UtilityType` and either (1) list all possible method keys and use **show if** so each utility only sees its `available_methods`, or (2) keep separate blocks per utility. Do not assume one block with identical fields for all. |
| **Single generic block for utility details** (summary + show if) | Same idea: one block with **show if** conditions that use `x` (e.g. `x.has_any_method()` or `report.get_missing_doc_labels_for_utility(utility_key)`). You need a way to get `utility_key` from `x` (e.g. `x.key` is set in `utilities_matrix_initialized`). Safe if conditions mirror current per-utility logic. |
| **One review entry for all drawings** (instead of 10 Edit lines) | DocAssemble does not support “review: - Edit: report.drawings[i]” with `i` in range as a literal loop in YAML. The supported pattern is a [review table](https://docassemble.org/docs/groups) with `rows: report.drawings` and `edit: True` and columns for the attributes to edit (e.g. file, title, format). So the fix is: **replace the 10 manual “Edit: report.drawings[0].file” … “Edit: report.drawings[9].file” with one `table:` review entry**, e.g. `table: report.drawings` with appropriate columns and edit buttons. Test that clicking Edit goes to the correct drawing question and that “Drawing N” labeling still works (e.g. via column content or row index). |
| **Remove duplicate address autocomplete script** (Job Information script) | The initial block uses delegated handlers (`$(document).on('input', _addrSelector, ...)`), so it should work for any matching field that exists when the user types. DocAssemble [initial blocks run on every screen load](https://docassemble.org/docs/logic); the script is part of that block. **Before relying only on the initial block:** confirm in testing that address autocomplete works on the Job Information page (where Site Address is first shown). If the field is rendered after the initial script runs or under a different name, the duplicate may have been added for DOM timing; in that case keep a minimal re-bind on that screen instead of the full duplicate. |

### Naming and structural suggestions (low risk)

| Suggestion | Note |
|------------|------|
| **Rename completion flags** (`hours_entered` → `hours_complete`, etc.) | Safe only if **every** reference is updated: `continue button field:`, mandatory block, and review. Current refs: `report.time_entries[i].hours_entered`, `report.cover_photo_complete`, `report.photo_pages[i].page_complete`, and mandatory/list logic. Optional; consistency only. |
| **Split `format_time_12hr()`** into helpers | Pure Python refactor; no DocAssemble API. Safe. |

### Summary

- **Do not** implement generic utility (methods/details) blocks by forcing one identical question for all utilities; use **show if** and/or `x.available_methods` so behavior per utility type is unchanged.
- **Do** implement review-drawings consolidation via a **table** with `rows: report.drawings`, not via a non-existent “review loop” over `i`.
- **Verify** address autocomplete after removing the Job Information duplicate (and retain a minimal bind on that page if needed).
- All other audit suggestions above are consistent with DocAssemble docs and, when applied as described, should not break existing functionality.
