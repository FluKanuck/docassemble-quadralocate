# Site Locate Report

---

**Prepared For:** {{ report.client_company }}

**Quadra Job Number:** {{ report.quadra_job_number }}

**Prepared By:** {{ report.technician_name }}

**Site Visit Date:** {{ format_date(report.site_visit_date) }}

**Site Address:**
{{ report.site_address }}

**Sheet Version:** 15rev7 | Issued {{ format_date(today()) }}

---

# Utility Locating

**BC 1 Call Number:** {{ report.format_bc1_display() }}

{% if not report.job.is_multi_day and defined('report.weather') %}
**Weather Conditions:** {{ report.weather }}
{% elif report.job.is_multi_day and report.job.work_days %}
**Weather Conditions:** {% for day in report.job.work_days %}{% if day.weather %}{{ format_date(day.date, format='short') }}: {{ day.weather }}{% if not loop.last %}; {% endif %}{% endif %}{% endfor %}
{% endif %}

---

## Billing Details

{{ report.format_billing_details() }}

---

## Summary of Work Performed

{{ report.format_combined_report() }}

---

{% if defined('report.client_po_number') and report.client_po_number %}
**Client PO Number:** {{ report.client_po_number }}
{% endif %}

{% if defined('report.client_job_number') and report.client_job_number %}
**Client Job Number:** {{ report.client_job_number }}
{% endif %}

{% if defined('report.client_rep_name') and report.client_rep_name %}
**Client Representative:** {{ report.client_rep_name }}
{% endif %}

{% if report.client_signature %}
**Client Signature:**

{{ report.client_signature }}
{% endif %}

---

**Missing Utility Documentation:**
{% if report.missing_docs.get('hydro') %}☑{% else %}☐{% endif %} BC Hydro (Electrical)
{% if report.missing_docs.get('comm') %}☑{% else %}☐{% endif %} Telus/Rogers/Shaw (Comm.)
{% if report.missing_docs.get('gas') %}☑{% else %}☐{% endif %} Fortis (Gas)
{% if report.missing_docs.get('municipal') %}☑{% else %}☐{% endif %} Municipal (Water, Stm, Sani.)
{% if report.missing_docs.get('pipeline') %}☑{% else %}☐{% endif %} Pipelines
{% if report.missing_docs.get('asbuilts') %}☑{% else %}☐{% endif %} As-builts

---

# Photos and Comments

{% if report.photo_pages and report.num_photo_pages > 0 %}
{% for photo_page in report.photo_pages %}
{% if photo_page.has_content() %}

## Photo Page {{ photo_page.page_number }}

{% if photo_page.photos %}
{% for photo in photo_page.photos %}
{{ photo }}

{% endfor %}
{% endif %}

{% if photo_page.comments %}
{{ photo_page.comments }}
{% endif %}

---

{% endif %}
{% endfor %}
{% endif %}

# Locate Drawings

{% if report.drawings and report.num_drawings > 0 %}
{% for drawing in report.drawings %}
{% if drawing.file %}

## {{ drawing.title if drawing.title else "Drawing " + drawing.page_number|string }}
{% if drawing.is_large_format() %}
*Large Format Drawing (11x17 / Tabloid)*
{% endif %}

{{ drawing.file }}

*This locate drawing and utility markings are valid for 30 days from date of locate or until ground markings are no longer visible, whichever comes sooner. Quadra Utility Locating Ltd. will not accept any liability for damages incurred as a result of this utility locate and the utility locate drawing.*

---

{% endif %}
{% endfor %}
{% endif %}

# Drawing Legend

## Located Utility | Unlocated Utility | BH/MW Location | Scanned Area

## APWA Uniform Colour Code:

| Colour | Meaning |
|--------|---------|
| White | Proposed Excavation |
| Pink | Temporary Survey Markings / Unidentified Utility |
| Red | Electrical, BC Hydro, Street lighting, Electrical Conduit |
| Yellow | Gas, Oil, Steam, Petroleum, or Gaseous Materials |
| Orange | Communication, Alarm or Signal Lines, Cables or Conduit |
| Blue | Potable Water |
| Purple | Reclaimed Water, Irrigation and Slurry Lines |
| Green | Sewers and Drain Lines |

---

## QUADRA UTILITY LOCATING LIMITED SITE LOCATE REPORT DISCLAIMER

Any damage MUST be reported to Quadra Utility Locating Ltd. at 1-604-897-4616 within 24 hours of a utility line strike. Quadra Utility Locating Ltd. will initiate a line strike investigation report. By accepting this locate report, you acknowledge and agree to all terms and conditions outlined.

This Locate drawing and utility markings are valid for 30 days from date of the locate or until locate marks are no longer visible, whichever is soonest.

Quadra Utility Locating Ltd. will not accept any liability for damages incurred as a result of this utility locate and the utility locate drawing provided.

This locate sketch is not to-scale and is not a surveyed drawing. It is a general representation of the identified buried utility lines and other relevant site features. The locations and depths of all marked utilities on the ground and indicated on this drawing are approximate. The exact location and depth of any utility can only be determined by physically exposing the utility or by contacting the utility owner. There is a potential risk for unlocated or abandoned utilities within the work area that are not indicated on this drawing. Any possible unlocated utilities within the work area may be due to varying geophysical interruptions that cause interference such as but not limited to ground conditions, and size/material of the utility.

According to Worksafe BC Practices "The hand expose zone is a distance 1m either side of the locate marks within which excavation with mechanical equipment must not take place, until the buried facility has been hand exposed and is clearly visible". The Ground Disturber, whether it be an individual, or company completing the ground disturbance is responsible for ensuring they can work safely around any and all utilities. Where single lines are shown it is possible multiple lines exist. (Expose 1.5m each side of the last line found in order to confirm the exact number of lines in the trench).

Quadra Utility Locating recommendation is to stay 2m from all paint markings if a utility will not be exposed. There should be no ground disturbance prior to contacting and receiving clearance from all private utility owners. This includes obtaining required permits for ground disturbance in proximity to an underground utility.

---

### LOCATOR PAINT MARKINGS

The locate marks provided of buried utilities are temporary and if they will be disturbed or destroyed by either the ground disturbers activities or the weather, the ground disturber must provide more permanent or offset marks or references that will not be disturbed. If the locate sketch should not coincide with the marks on the ground, a new locate request must be obtained. Any changes to the work area should it extend beyond the marked area swept requires a new locate request. The excavator is responsible for the removal of all the flags or other marks upon completion of the excavation activities.

### GROUND DISTURBER CAUTION

Pink area represents a one metre buffer zone around any marked utility. Excavating within one metre of locate marks must be done by non-destructive methods such as hand digging or hydro-vaccing. Depths provided are always approximate and can only be verified by exposing the utility.

### LIFE SPAN OF THE LOCATE

1. This Locate drawing and utility markings are valid for 30 days from date of the locate.
2. Original Locate marks must be visible or the ground disturber must provide more permanent markings or references or the facility has been hand exposed or hydrovac exposed.
3. Ground disturber's activity at the site has not been interrupted except for a maximum 4 calendar day period over weekends more if weather dictates longer interruptions.
4. Ground disturber's presence at the site remains evident during such interruptions.
5. For further details on the BC Common Ground Alliance Best Practices, visit: https://commongroundalliance.com/Publications-Media/Best-Practices-Guide

Refer to BC WCB Regulation 20.79 (Excavations, Underground Utilities) when performing subsurface work near buried utilities. "Excavation or drilling work in proximity to an underground utility service must be undertaken in conformity with the requirements of the owner of that utility service."
