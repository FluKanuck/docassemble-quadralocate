# Quadra Locate Report — Interview Flow Planning Document

This document outlines the complete flow of the docassemble interview in [docassemble/quadralocate/data/questions/locate_report.yml](docassemble/quadralocate/data/questions/locate_report.yml), including all questions and possible branches.

---

## 1. High-level flow

```mermaid
flowchart TD
  subgraph entry [Entry]
    Start[Quadra Utility Locate Report]
    Start --> Action{report_action}
    Action -->|Start New Report| JobInfo[Job Information]
    Action -->|Resume Existing Job| Resume[Resume: Quadra Job Number]
    Action -->|Edit Submitted Report| Edit[Edit: Quadra Job Number]
    Resume --> JobInfo
    Edit --> JobInfo
  end

  subgraph main [Main interview]
    JobInfo --> BC1[BC 1 Call Information]
    BC1 --> ClientInfo[Client Information]
    ClientInfo --> PreparedBy[Prepared By]
    PreparedBy --> TimeTable1[Time on Site - Who was on site when]
    TimeTable1 --> MoreTime{Any more time entries?}
    MoreTime -->|Yes| TimeTable1
    MoreTime -->|No| Weather[Weather Conditions]
    Weather --> HourBreakdown[Hour breakdown per entry]
    HourBreakdown --> Supplemental[Supplemental Charges]
    Supplemental --> Materials[Materials Used]
    Materials --> PropertyType[Property Type]
    PropertyType --> Utilities[Utility Matrix - 8 types]
    Utilities --> UtilDetails[Utility Details - conditional]
    UtilDetails --> SiteConditions[Site Conditions]
    SiteConditions --> TravelNotes[Travel Notes]
    TravelNotes --> Hydrovac[Hydrovac Recommendation]
    Hydrovac --> HydrovacReasons{Hydrovac recommended?}
    HydrovacReasons -->|Yes| HydrovacReasonsQ[Hydrovac Reasons]
    HydrovacReasons -->|No| MissingDocs[Missing Documentation]
    HydrovacReasonsQ --> MissingDocs
    MissingDocs --> Recommendations[Recommendations]
    Recommendations --> Photos[Site Photos - count]
    Photos --> PhotoPages[Photo Page 1..N]
    PhotoPages --> DrawingsCount[Locate Drawings - count]
    DrawingsCount --> Drawings[Drawing 1..N]
    Drawings --> Signature[Client Representative Signature]
    Signature --> Review[Review Your Report]
    Review --> ReviewChoice{review_complete}
    ReviewChoice -->|Go Back and Edit| main
    ReviewChoice -->|Generate Report| Final[Report Generated Successfully]
  end

  Final --> Download[Download PDF]
  Final --> EditReport[Edit This Report]
  Final --> NewReport[Start New Report]
```

---

## 2. Sections (navigation order)

The interview is divided into these sections (from `sections:` in the YAML):

| Section key   | Display name        |
|---------------|---------------------|
| introduction  | Introduction        |
| job_info      | Job Information     |
| time_billing  | Time & Billing      |
| utilities     | Utility Locating    |
| details       | Locate Details      |
| hydrovac      | Hydrovac            |
| recommendations | Recommendations   |
| media         | Photos & Drawings   |
| signatures    | Signatures          |
| review        | Review & Export     |

---

## 3. Entry-point branches

**Single question:** *Quadra Utility Locate Report* (field: `report_action`)

- **Start New Report** (`new`) → proceed to Job Information.
- **Resume Existing Job** (`resume`) → show *Resume Existing Job* (one field: Quadra Job Number `resume_job_number`), then proceed to Job Information.
- **Edit Submitted Report** (`edit`) → show *Edit Submitted Report* (one field: Quadra Job Number `edit_job_number`), then proceed to Job Information.

*(Resume/Edit currently only collect the job number; loading existing report data would be implemented separately, e.g. session or database.)*

---

## 4. Question list and branches (in interview order)

### 4.1 Introduction

| # | Question / block           | Fields / behavior | Branch / condition |
|---|----------------------------|-------------------|--------------------|
| 1 | Quadra Utility Locate Report | `report_action` (buttons) | Always first. |
| 2 | Resume Existing Job        | `resume_job_number` | **Show if** `report_action` is `resume`. |
| 3 | Edit Submitted Report      | `edit_job_number`  | **Show if** `report_action` is `edit`. |

---

### 4.2 Job Information

| # | Question            | Fields | Branch |
|---|---------------------|--------|--------|
| 4 | Job Information     | Client Company, Quadra Job Number, Site Address, Site Visit Date | Always. |
| 5 | BC 1 Call Information | BC 1 Call Provider (None/Quadra/Client), BC 1 Call Number | Always. BC 1 Call Number has **js show if**: provider != "None". |
| 6 | Client Information  | Client Representative Name, Client PO Number, Client Job Number (all optional) | Always. |
| 7 | Prepared By         | Technician Name | Always. |

---

### 4.3 Time & Billing

| # | Question / block | Fields / behavior | Branch |
|---|------------------|-------------------|--------|
| 8 | Time on Site — Who was on site when | List: Date, Technician Name, Start Time, End Time (per row). `list collect: True`. | At least one entry; then loop. |
| 9 | Any more time entries to add? | `report.time_entries.there_is_another` (yes/no) | **Show if** at least 1 time entry. **Branch:** Yes → back to question 8; No → continue. |
|10 | Weather Conditions | Weather (optional) | Always. |
|11 | Hour breakdown — [date] — [technician] | Per entry: EM, GPR, Travel, GPS Survey, RTS Survey, 2Hr Min, Orientations, Sketch Drafting, Ferry Standby, Camera Inspection (all optional/default 0) | One screen per time entry (index `i`). |
|12 | Supplemental Charges | Parking ($), Traffic Control, Permitting, LOA, Desktop Review, AutoCAD, Concrete Coring, Vapour Probes, Data Processing (all optional) | Always. |
|13 | Materials Used      | Pin Flags, Lathe 24", Lathe 48", KMs Driven (all optional) | Always. |
|14 | Property Type       | `report.property_type` (Private / Public / Both) | Always. |

---

### 4.4 Utility Locating (matrix)

Eight utility blocks; each asks for locate methods (yes/no). **Order:** Electrical → Communications → Gas → Water → Storm → Sanitary → Ditch → Unknown/Other.

| # | Question              | Methods / fields | Branch |
|---|-----------------------|------------------|--------|
|15 | Electrical Utilities  | EM, GPR, Visual, Not Located, Not in Proposed Work Area | Always. |
|16 | Communications Utilities | Same 5 methods | Always. |
|17 | Gas / Pipeline Utilities | Same 5 methods | Always. |
|18 | Water Utilities       | Same 5 methods | Always. |
|19 | Storm Utilities       | Same 5 methods | Always. |
|20 | Sanitary Utilities    | Same 5 methods | Always. |
|21 | Ditch                 | Visual, Not Located only | Always. |
|22 | Unknown / Other Utilities | Same 5 methods as Electrical | Always. |

---

### 4.5 Locate Details (conditional)

Each details block is **shown only if** that utility type has at least one method selected (`has_any_method()`). Storm and Sanitary share one details question.

| # | Question                    | Fields | Branch |
|---|-----------------------------|--------|--------|
|23 | Electrical Details         | Electrical Summary (optional area) | **Show if** `report.utilities.electrical.has_any_method()`. |
|24 | Communications Details     | Communications Summary | **Show if** communications has any method. |
|25 | Gas / Pipeline Details     | Gas / Pipeline Summary | **Show if** gas has any method. |
|26 | Water Details              | Water Summary | **Show if** water has any method. |
|27 | Storm and Sanitary Details | Storm and Sanitary Summary (`report.storm_sanitary_summary`) | **Show if** storm **or** sanitary has any method. |
|28 | Unknown / Other Details    | Unknown / Other Summary | **Show if** unknown has any method. |
|29 | Site Conditions            | Site Conditions (optional area) | Always. |
|30 | Travel Notes               | Travel Notes (optional area) | Always. |

---

### 4.6 Hydrovac

| # | Question              | Fields | Branch |
|---|-----------------------|--------|--------|
|31 | Hydrovac Recommendation | Is Hydrovac recommended? (yes/no) | Always. |
|32 | Hydrovac Reasons      | Obstructions, Unlocated utilities, Deep utilities, No documentation, Additional notes | **Show if** `report.hydrovac.recommended` is true. |

---

### 4.7 Recommendations

| # | Question               | Fields | Branch |
|---|------------------------|--------|--------|
|33 | Missing Documentation | BC Hydro, Communications, Fortis, Municipal, Pipeline, As-builts (each yes/no) | Always. |
|34 | Recommendations       | Recommendations (optional area) | Always. |

---

### 4.8 Photos & Drawings

| # | Question        | Fields / behavior | Branch |
|---|-----------------|-------------------|--------|
|35 | Site Photos     | Number of photo pages (0–10, default 1) | Always. |
|36 | Photo Page i    | Photos (files), Comments (optional). One screen per page. | Repeat for `i = 0 .. num_photo_pages - 1` (if `num_photo_pages > 0`). |
|37 | Locate Drawings | Number of drawings (0–10, default 1) | Always. |
|38 | Drawing i       | Format (Normal / Large), Drawing file, Title. One screen per drawing. | Repeat for `i = 0 .. num_drawings - 1` (if `num_drawings > 0`). |

---

### 4.9 Signatures & Review

| # | Question / block | Fields / behavior | Branch |
|---|------------------|-------------------|--------|
|39 | Client Representative Signature | Client Rep Name (default from job info), Signature (optional) | Always. |
|40 | Review Your Report | Read-only summary; `review_complete` (Generate Report / Go Back and Edit) | Always. **Branch:** Generate Report → final screen; Go Back and Edit → re-run interview (user can change answers). |
|41 | Report Generated Successfully (event: final_screen) | Download PDF, Edit This Report, Start New Report, Exit | After generation. Edit increments `revision_number` and returns to review; New runs `new_session`. |

---

### 4.10 Save Progress (multi-day)

| # | Question     | Fields / behavior | Branch |
|---|-------------|-------------------|--------|
|42 | Save Progress | `progress_saved`: Continue Working / Save and Exit | Shown when user saves progress (multi-day); not in the main mandatory completion path. |

---

## 5. Summary of all branches

- **Entry:** 3-way (new / resume / edit). Resume and edit each add one question (job number).
- **Time entries:** Loop on "Any more time entries?" (Yes → add another row, then hour breakdown for that entry).
- **Hour breakdown:** One question per time entry (index `i`).
- **Utility details:** 6 conditional blocks (Electrical, Communications, Gas, Water, Storm+Sanitary, Unknown) based on `has_any_method()`.
- **Hydrovac reasons:** Shown only if Hydrovac is recommended.
- **Photo pages:** N questions where N = number of photo pages (0–10).
- **Drawings:** N questions where N = number of drawings (0–10).
- **Review:** Generate Report → final screen; Go Back and Edit → re-enter interview.
- **Final screen:** Download, Edit Report (revision), Start New Report, Exit.

---

## 6. Where this is implemented

- **Interview logic and all questions:** [docassemble/quadralocate/data/questions/locate_report.yml](docassemble/quadralocate/data/questions/locate_report.yml)  
  - Mandatory completion order: lines 557–616 (mandatory block).
- **Conditional helpers (e.g. `has_any_method()`):** [docassemble/quadralocate/objects.py](docassemble/quadralocate/objects.py) (`UtilityType`, `LocateReport`, etc.).
