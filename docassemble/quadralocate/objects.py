"""
Custom Python objects for Quadra Utility Locate Report
"""
from docassemble.base.util import DAObject, DAList, DADict, format_time, format_date
from datetime import datetime, time
import os
import json
import logging

log = logging.getLogger(__name__)


__all__ = [
    'UtilityType',
    'UtilityMatrix',
    'Technician',
    'TimeEntry',
    'WorkDay',
    'MultiDayJob',
    'HydrovacRecommendation',
    'PhotoPage',
    'Drawing',
    'LocateReport',
    'HoursDict',
    'time_15min_choices',
    'format_time_12hr',
    'DropboxService',
    'JobMapService',
    'ReportArchiver',
]


class UtilityType(DAObject):
    """Represents a single utility type with its locate methods and summary."""
    
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        self.initializeAttribute('methods', DADict)
        # Default method options
        if not hasattr(self, 'available_methods'):
            self.available_methods = ['em', 'gpr', 'visual', 'not_located', 'not_in_area']
    
    def has_any_method(self):
        """Check if any locate method is selected."""
        for method in self.available_methods:
            if self.methods.get(method, False):
                return True
        return False
    
    def is_not_in_scope(self):
        """Check if this utility is marked as not in scope."""
        return bool(self.methods.get('not_in_scope', False))
    
    def should_display(self):
        """Determine if this utility section should appear in report.
        
        Returns False if the only selected method is 'none_in_area' (used by ditch)
        so the utility is excluded from the combined report entirely.
        """
        # If the only method selected is 'none_in_area', exclude from report
        if self.methods.get('none_in_area', False):
            other_methods = [m for m in self.available_methods if m != 'none_in_area']
            if not any(self.methods.get(m, False) for m in other_methods):
                return False
        return self.has_any_method() or (hasattr(self, 'summary') and self.summary)
    
    def get_method_labels(self):
        """Get list of human-readable method labels for selected methods."""
        labels = []
        method_label_map = {
            'em': 'Located with EM',
            'gpr': 'Located with GPR',
            'visual': 'Located visually',
            'not_located': 'Not located',
            'not_in_area': 'Not in proposed work area',
            'not_in_scope': 'Not in scope',
            'none_in_area': 'None in area',
            'opened_cb_mh': 'Opened Catchbasins/Manholes',
            'unable_open_cb_mh': 'Unable to Open Catchbasins/Manholes',
            'opened_mh': 'Opened Manholes',
            'unable_open_mh': 'Unable to Open Manholes',
        }
        for method in self.available_methods:
            if self.methods.get(method, False):
                labels.append(method_label_map.get(method, method))
        return labels
    
    def format_header(self):
        """Format the utility header with methods in parentheses."""
        header = self.display_name.upper()
        labels = self.get_method_labels()
        if labels:
            header += " (" + ", ".join(labels) + ")"
        return header
    
    def format_section(self):
        """Format the complete section for report output."""
        if not self.should_display():
            return ""
        header = self.format_header()
        summary = getattr(self, 'summary', '') or ''
        return f"{header}:\r{summary}" if summary else f"{header}:"


class UtilityMatrix(DAObject):
    """Collection of all utility types for the locate report."""
    
    UTILITY_TYPES = [
        ('electrical', 'Electrical', ['em', 'gpr', 'visual', 'not_located', 'not_in_area', 'not_in_scope']),
        ('communications', 'Communications', ['em', 'gpr', 'visual', 'not_located', 'not_in_area', 'not_in_scope']),
        ('gas', 'Gas / Pipeline', ['em', 'gpr', 'visual', 'not_located', 'not_in_area', 'not_in_scope']),
        ('water', 'Water', ['em', 'gpr', 'visual', 'not_located', 'not_in_area', 'not_in_scope']),
        ('storm', 'Storm', ['em', 'gpr', 'visual', 'not_located', 'not_in_area', 'not_in_scope', 'opened_cb_mh', 'unable_open_cb_mh']),
        ('sanitary', 'Sanitary', ['em', 'gpr', 'visual', 'not_located', 'not_in_area', 'not_in_scope', 'opened_mh', 'unable_open_mh']),
        ('ditch', 'Ditch', ['visual', 'not_located', 'none_in_area']),
        ('unknown', 'Unknown / Other', ['em', 'gpr', 'visual', 'not_located', 'not_in_area', 'not_in_scope']),
    ]
    
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        # Do NOT access children (e.g. getattr(self, key)) here: that would require
        # report.utilities.electrical etc. while report.utilities is still being created,
        # causing an infinite loop. Children are initialized in a separate code block
        # (utilities_matrix_initialized) after report.utilities exists.
    
    def get_active_utilities(self):
        """Return list of utilities that should appear in report."""
        active = []
        for key, _, _ in self.UTILITY_TYPES:
            utility = getattr(self, key)
            if utility.should_display():
                active.append(utility)
        return active
    
    def get_not_in_scope_utilities(self):
        """Return display names of all utilities marked as not in scope."""
        names = []
        for key, display_name, _ in self.UTILITY_TYPES:
            utility = getattr(self, key)
            if utility.is_not_in_scope():
                names.append(display_name)
        return names


# Hour types and labels shared by Technician and TimeEntry (10 types; two_hr_min is Yes/No)
HOUR_TYPES = ['em', 'gpr', 'travel', 'gps_survey', 'rts_survey', 'two_hr_min', 'orientations', 'sketch_drafting', 'ferry_standby', 'camera_inspection']
HOUR_LABELS = {
    'em': 'EM',
    'gpr': 'GPR',
    'travel': 'Travel',
    'gps_survey': 'GPS Survey',
    'rts_survey': 'RTS Survey',
    'two_hr_min': '2Hr Min',
    'orientations': 'Orientations',
    'sketch_drafting': 'Sketch Drafting',
    'ferry_standby': 'Ferry Standby',
    'camera_inspection': 'Camera Inspection',
}
HOUR_TYPES_NUMERIC = [k for k in HOUR_TYPES if k != 'two_hr_min']
REPORT_MAIN_COMBINED_MAX_CHARS = 2500
REPORT_MAIN_BILLING_MAX_CHARS = 1100
REPORT_CONT_PAGE_MAX_CHARS = 3400


class HoursDict(dict):
    """Plain dict — not a DADict — so docassemble never enters the gather protocol.
    Class-level there_are_any and gathered prevent any residual Docassemble lookups."""
    there_are_any = True
    gathered = True


class TimeEntry(DAObject):
    """One row in Table 1: date, technician name, start/end time; hours filled in Table 2."""
    
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        # Use HoursDict (plain dict) instead of DADict to completely bypass
        # Docassemble's gather protocol (there_are_any / gathered / new_item_name).
        # DADict.__setitem__ resets gathered=False on every key assignment, making it
        # impossible to keep gathered=True — the root cause of ISS-014 and ISS-015.
        if not hasattr(self, 'hours'):
            self.hours = HoursDict()
            for hour_type in HOUR_TYPES:
                self.hours[hour_type] = 0 if hour_type != 'two_hr_min' else False
    
    def format_time_range_12hr(self):
        """Format start/end times as '8:00 AM - 2:00 PM' for display in titles."""
        start = format_time_12hr(getattr(self, 'start_time', None))
        end = format_time_12hr(getattr(self, 'end_time', None))
        if start and end:
            return f"{start} - {end}"
        elif start:
            return f"from {start}"
        elif end:
            return f"to {end}"
        return ""


class Technician(DAObject):
    """Represents a technician with their hours breakdown."""
    
    HOUR_TYPES = HOUR_TYPES
    HOUR_LABELS = HOUR_LABELS
    
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        # Use HoursDict (plain dict) — same rationale as TimeEntry (ISS-015).
        # The build code later replaces this with HoursDict(hours_vals) anyway.
        if not hasattr(self, 'hours'):
            self.hours = HoursDict()
            for hour_type in self.HOUR_TYPES:
                self.hours[hour_type] = 0 if hour_type != 'two_hr_min' else False

    def has_any_hours(self):
        """Check if technician has any hours or 2Hr Min recorded."""
        for hour_type in HOUR_TYPES_NUMERIC:
            if (self.hours.get(hour_type, 0) or 0) > 0:
                return True
        if self.hours.get('two_hr_min'):
            return True
        return False
    
    def get_total_hours(self):
        """Calculate total hours for this technician (numeric types only)."""
        total = 0
        for hour_type in HOUR_TYPES_NUMERIC:
            total += float(self.hours.get(hour_type, 0) or 0)
        return total
    
    def format_hours_line(self):
        """Format hours as 'EM = 2; GPR = 1.5; 2Hr Min = Yes; ...'."""
        parts = []
        for hour_type in HOUR_TYPES_NUMERIC:
            value = self.hours.get(hour_type)
            if value and float(value) > 0:
                label = self.HOUR_LABELS.get(hour_type, hour_type)
                parts.append(f"{label} = {format_number(float(value))}")
        return "; ".join(parts)
    
    def format_tech_line(self):
        """Format complete technician line with name and hours."""
        name = getattr(self, 'name', 'Unknown')
        hours_str = self.format_hours_line()
        if hours_str:
            return f"{name}: {hours_str}"
        return name


class WorkDay(DAObject):
    """Represents a single work day in a multi-day job."""
    
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        self.initializeAttribute('technicians', DAList.using(object_type=Technician, there_are_any=True, complete_attribute='name'))
    
    def format_time_range(self):
        """Format start to end time as '9:30 am to 4:15 pm'."""
        start = format_time_12hr(getattr(self, 'start_time', None))
        end = format_time_12hr(getattr(self, 'end_time', None))
        
        if start and end:
            return f"{start} to {end}"
        elif start:
            return f"from {start}"
        elif end:
            return f"to {end}"
        return ""
    
    def get_all_hours_by_type(self):
        """Sum all technician hours by type for this day (two_hr_min: True if any)."""
        totals = {ht: 0 for ht in Technician.HOUR_TYPES}
        totals['two_hr_min'] = False
        for tech in self.technicians:
            for hour_type in HOUR_TYPES_NUMERIC:
                totals[hour_type] += float(tech.hours.get(hour_type, 0) or 0)
            if tech.hours.get('two_hr_min'):
                totals['two_hr_min'] = True
        return totals


class MultiDayJob(DAObject):
    """Manages multi-day job with multiple work days."""
    
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        self.initializeAttribute('work_days', DAList.using(object_type=WorkDay, there_are_any=True, complete_attribute='date'))
        self.is_multi_day = False
    
    def get_all_technicians(self):
        """Get unique list of all technicians across all days."""
        tech_dict = {}
        for day in self.work_days:
            for tech in day.technicians:
                name = getattr(tech, 'name', 'Unknown')
                if name not in tech_dict:
                    tech_dict[name] = {'hours': {ht: 0 for ht in Technician.HOUR_TYPES}}
                    tech_dict[name]['hours']['two_hr_min'] = False
                for hour_type in HOUR_TYPES_NUMERIC:
                    tech_dict[name]['hours'][hour_type] += float(tech.hours.get(hour_type, 0) or 0)
                if tech.hours.get('two_hr_min'):
                    tech_dict[name]['hours']['two_hr_min'] = True
        return tech_dict
    
    def get_combined_totals(self):
        """Get combined hour totals across all days and technicians."""
        totals = {ht: 0 for ht in Technician.HOUR_TYPES}
        totals['two_hr_min'] = False
        for day in self.work_days:
            day_totals = day.get_all_hours_by_type()
            for hour_type in HOUR_TYPES_NUMERIC:
                totals[hour_type] += day_totals[hour_type]
            if day_totals.get('two_hr_min'):
                totals['two_hr_min'] = True
        return totals
    
    def format_time_on_site(self):
        """Format TIME ON SITE section for single or multi-day."""
        if not self.is_multi_day or len(self.work_days) <= 1:
            # Single day format
            if self.work_days:
                day = self.work_days[0]
                return day.format_time_range()
            return ""
        
        # Multi-day format
        lines = []
        for day in self.work_days:
            date_str = format_date(day.date, format='short') if hasattr(day, 'date') else 'Unknown'
            time_range = day.format_time_range()
            lines.append(f"Day ({date_str}): {time_range}")
        return "\r".join(lines)
    
    def format_type_time(self):
        """Format TYPE/TIME section with per-tech or per-day breakdown."""
        lines = []

        if not self.is_multi_day or len(self.work_days) <= 1:
            # Single day - list technicians
            if self.work_days:
                for tech in self.work_days[0].technicians:
                    if tech.has_any_hours():
                        lines.append(tech.format_tech_line())
                
                # Add totals if 2+ technicians
                if len([t for t in self.work_days[0].technicians if t.has_any_hours()]) >= 2:
                    totals = self.work_days[0].get_all_hours_by_type()
                    totals_line = format_totals_line(totals)
                    if totals_line:
                        lines.append(f"Total: {totals_line}")
        else:
            # Multi-day - show daily breakdown
            for day_idx, day in enumerate(self.work_days):
                date_str = format_date(day.date, format='short') if hasattr(day, 'date') else 'Unknown'
                tech_parts = []
                for tech_idx, tech in enumerate(day.technicians):
                    if tech.has_any_hours():
                        tech_parts.append(tech.format_tech_line())
                if tech_parts:
                    lines.append(f"Day ({date_str}): " + " | ".join(tech_parts))
            
            # Add combined totals
            all_techs = self.get_all_technicians()
            if all_techs:
                lines.append("")
                lines.append("TOTALS:")
                for name, data in all_techs.items():
                    tech_total = format_totals_line(data['hours'])
                    if tech_total:
                        lines.append(f"  {name}: {tech_total}")
                
                combined = self.get_combined_totals()
                combined_line = format_totals_line(combined)
                if combined_line:
                    lines.append(f"  Combined: {combined_line}")
        
        return "\r".join(lines)


class HydrovacRecommendation(DAObject):
    """Manages Hydrovac recommendation with reasons."""
    
    STANDARD_REASONS = [
        ('obstructions', 'Obstructions in scan area'),
        ('unlocated', 'Unlocated utilities in area'),
        ('deep_utilities', 'Possible utilities in area deeper than the scan capabilities due to geophysical subsurface conditions'),
        ('no_documentation', 'No BC One Call/Site Plans/As-Builts for the area'),
    ]
    
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        self.initializeAttribute('reasons', DADict)
        # Do NOT set self.recommended here — it must remain undefined so
        # Docassemble shows the question. Setting it to False in init()
        # causes the mandatory block to skip the hydrovac question entirely.
        self.custom_notes = ""
    
    def get_selected_reasons(self):
        """Get list of selected reason texts."""
        selected = []
        for key, text in self.STANDARD_REASONS:
            if self.reasons.get(key, False):
                selected.append(text.lower())  # lowercase for sentence flow
        return selected
    
    def format_section(self):
        """Format the complete Hydrovac recommendation section."""
        if not self.recommended:
            return ""
        
        selected = self.get_selected_reasons()
        
        output = "HYDROVAC RECOMMENDED:\r"
        
        if selected:
            reasons_text = oxford_join(selected)
            output += f"Hydrovac exposure is recommended due to: {reasons_text}."
        else:
            output += "Hydrovac exposure is recommended."
        
        if self.custom_notes:
            output += f"\r{self.custom_notes}"
        
        return output


class PhotoPage(DAObject):
    """Represents a page of up to 6 photos with individual captions."""
    
    SLOTS = range(1, 7)  # 1-6
    
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        # Do NOT set photo_1..photo_6 or comment_1..comment_6 here —
        # they must remain undefined so Docassemble shows the question.
    
    def get_photos_with_comments(self):
        """Yield (slot_number, photo, comment) for each slot that has an uploaded photo."""
        for n in self.SLOTS:
            photo = getattr(self, f'photo_{n}', None)
            if photo:
                yield n, photo, getattr(self, f'comment_{n}', '') or ''
    
    def has_content(self):
        """Check if any slot has an uploaded photo."""
        return any(True for _ in self.get_photos_with_comments())
    
    def photo_count(self):
        """Return the number of photos uploaded on this page."""
        return sum(1 for _ in self.get_photos_with_comments())
    
    def get_photo_fields(self, page_index, job_number=''):
        """Return dict mapping PDF form field names to values for this photo page.
        
        Uses _extract_file() to convert DAFileList → single DAFile, then passes
        [FILE ref] format. PDF template must use Signature (/Sig) fields for images.
        """
        fields = {
            'quadra_job_number': str(job_number),
            'page_label': f'Photo Page {page_index + 1}',
        }
        for n in self.SLOTS:
            raw = getattr(self, f'photo_{n}', None)
            photo_val = _to_pdf_file_value(raw, f'photo_{n}')
            if photo_val:
                fields[f'photo_{n}'] = photo_val
            caption = getattr(self, f'comment_{n}', '') or ''
            fields[f'caption_{n}'] = caption
        return fields


class Drawing(DAObject):
    """Represents a locate drawing with format specification."""
    
    FORMAT_NORMAL = 'normal'
    FORMAT_LARGE = 'large'
    
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        # Do NOT set self.file, self.format, or self.title here — they must
        # remain undefined so Docassemble shows the drawing upload question.
    
    def is_large_format(self):
        """Check if this is a large format drawing."""
        return self.format == self.FORMAT_LARGE
    
    def get_format_label(self):
        """Get human-readable format label."""
        if self.format == self.FORMAT_LARGE:
            return "Large Format (11x17)"
        return "Normal (Letter/A4)"

    def has_content(self):
        """Check if this drawing has an uploaded file."""
        return bool(_extract_file(getattr(self, 'file', None)))

    def get_file_for_preview(self):
        """Return uploaded drawing file for preview display."""
        return _extract_file(getattr(self, 'file', None))
    
    def get_drawing_fields(self, job_number=''):
        """Return dict mapping PDF form field names to values for this drawing."""
        fields = {
            'quadra_job_number': str(job_number),
            'drawing_title': getattr(self, 'title', '') or '',
        }
        drawing_val = _to_pdf_file_value(getattr(self, 'file', None), 'drawing_image')
        if drawing_val:
            fields['drawing_image'] = drawing_val
        return fields


class LocateReport(DAObject):
    """Main report object that aggregates all components."""
    MISSING_DOC_LABELS = {
        'hydro': 'BC Hydro',
        'comm': 'Communications',
        'gas': 'Fortis',
        'municipal': 'Municipal',
        'pipeline': 'Pipeline',
        'asbuilts': 'As-builts',
    }
    MISSING_DOC_UTILITY_MAP = {
        'electrical': ['hydro'],
        'communications': ['comm'],
        'gas': ['gas', 'pipeline'],
        'water': ['municipal'],
        'storm': ['municipal'],
        'sanitary': ['municipal'],
    }
    MISSING_DOC_UTILITY_LABEL_OVERRIDES = {
        'communications': {
            'comm': 'Telecommunication providers',
        },
        'water': {
            'municipal': 'Water',
        },
        'storm': {
            'municipal': 'Storm',
        },
        'sanitary': {
            'municipal': 'Sanitary',
        },
    }
    
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        self.initializeAttribute('utilities', UtilityMatrix)
        self.initializeAttribute('job', MultiDayJob)
        self.initializeAttribute('hydrovac', HydrovacRecommendation)
        self.initializeAttribute('missing_docs', DADict)
        self.initializeAttribute('photo_pages', DAList.using(object_type=PhotoPage, auto_gather=False))
        self.initializeAttribute('drawings', DAList.using(object_type=Drawing, auto_gather=False))
        # Do NOT set num_photo_pages or num_drawings here — they must remain
        # undefined so Docassemble shows the "how many" questions.
        self.revision_number = 0
    
    def format_bc1_display(self):
        """Format BC 1 Call number with provider."""
        provider = getattr(self, 'bc1_provider', None)
        number = getattr(self, 'bc1_number', '')
        
        if provider == 'None':
            return "No BC 1 Call completed"
        elif provider == 'Client':
            suffix = " (Provided by Client)"
        elif provider == 'Quadra':
            suffix = " (Provided by Quadra)"
        else:
            suffix = ""
        
        if not number and not suffix:
            return ""
        elif not number:
            return suffix.strip(" ()")
        else:
            return f"{number}{suffix}"
    
    def format_missing_docs_sentence(self):
        """Generate missing documentation warning sentence."""
        missing = []
        for key, label in self.MISSING_DOC_LABELS.items():
            if self.missing_docs.get(key, False):
                missing.append(label)
        
        if not missing:
            return ""
        
        docs_list = oxford_join(missing)
        return (f"*{docs_list}* documentation missing on site. It is the responsibility "
                "of the Ground Disturber, prior to ground disturbance, to obtain and "
                "review said documentation.")

    def get_missing_doc_labels_for_utility(self, utility_key):
        """Return selected missing-doc labels mapped to a utility section."""
        labels = []
        utility_overrides = self.MISSING_DOC_UTILITY_LABEL_OVERRIDES.get(utility_key, {})
        for doc_key in self.MISSING_DOC_UTILITY_MAP.get(utility_key, []):
            if self.missing_docs.get(doc_key, False):
                label = utility_overrides.get(doc_key, self.MISSING_DOC_LABELS.get(doc_key, doc_key))
                labels.append(label)
        return labels

    def format_utility_missing_docs_sentence(self, utility_key):
        """Return utility-specific missing-doc sentence (if any)."""
        labels = self.get_missing_doc_labels_for_utility(utility_key)
        if not labels:
            return ""
        if utility_key in ['water', 'storm', 'sanitary'] and self.missing_docs.get('municipal', False):
            utility_label_map = {
                'water': 'Water',
                'storm': 'Storm',
                'sanitary': 'Sanitary',
            }
            utility_label = utility_label_map.get(utility_key, utility_key.title())
            return (
                f"No municipal GIS information for {utility_label} available at the time "
                "the utility locate was performed."
            )
        if utility_key == 'communications' and labels == ['Telecommunication providers']:
            return (
                "No BC1 Call information available from Telecommunication providers "
                "at the time the utility locate was performed."
            )
        utility_list = oxford_join(labels)
        return (
            f"No BC1 Call information available for {utility_list} at the time "
            "the utility locate was performed."
        )

    def format_utility_section_with_missing_docs(self, utility_key, utility):
        """Render a utility section with forced output for mapped missing docs."""
        has_missing_docs = bool(self.get_missing_doc_labels_for_utility(utility_key))
        should_display = utility.should_display()
        if not should_display and not has_missing_docs:
            return ""

        header = utility.format_header() if should_display else utility.display_name.upper()
        section_lines = []

        missing_sentence = self.format_utility_missing_docs_sentence(utility_key)
        if missing_sentence:
            section_lines.append(missing_sentence)

        summary = getattr(utility, 'summary', '') or ''
        if summary:
            section_lines.append(summary)

        if section_lines:
            return f"{header}:\r" + "\r".join(section_lines)
        return f"{header}:"
    
    def format_recommendations(self):
        """Format recommendations with auto-appended missing docs and not-in-scope warnings."""
        reco = getattr(self, 'recommendations', '') or ''
        missing_sentence = self.format_missing_docs_sentence()
        
        if missing_sentence:
            if reco:
                reco = f"{reco}\r\r{missing_sentence}"
            else:
                reco = missing_sentence
        
        # Dynamic not-in-scope warning (built from whichever utilities are marked)
        not_in_scope_names = self.utilities.get_not_in_scope_utilities()
        if not_in_scope_names:
            scope_list = oxford_join(not_in_scope_names)
            scope_sentence = (
                f"{scope_list} Utilities were not in the scope of work and thus not located. "
                "Confirm location before working near these potential utilities."
            )
            if reco:
                reco = f"{reco}\r\r{scope_sentence}"
            else:
                reco = scope_sentence
        
        if reco:
            return f"RECOMMENDATIONS:\r{reco}"
        return ""
    
    def format_billing_details(self):
        """Format the complete billing details section."""
        lines = []

        # TIME ON SITE
        time_on_site = self.job.format_time_on_site()
        if time_on_site:
            lines.append(make_line("TIME ON SITE", time_on_site))
        
        # TYPE/TIME
        type_time = self.job.format_type_time()
        if type_time:
            type_time_lines = type_time.split("\r")
            lines.append(make_line("TYPE/TIME", type_time_lines[0]))
            for extra_line in type_time_lines[1:]:
                lines.append(make_continuation_line(extra_line))
        
        # SUPPLEMENTAL
        supp_items = self.format_supplemental()
        if supp_items:
            lines.append(make_line("SUPPLEMENTAL", supp_items))
        
        # MATERIALS
        mat_items = self.format_materials()
        if mat_items:
            lines.append(make_line("MATERIALS", mat_items))
        
        # PROPERTY TYPE
        prop_type = self.format_property_type()
        if prop_type:
            lines.append(make_line("PROPERTY TYPE", prop_type))
        
        return "\r".join(lines)
    
    def format_supplemental(self):
        """Format supplemental charges with mixed boolean/hourly values."""
        items = []
        bool_fields = [
            ('traffic_control', 'Traffic control'),
            ('permitting', 'Permitting'),
        ]
        hourly_fields = [
            ('loa', 'LOA'),
            ('desktop', 'Desktop review'),
            ('cad', 'AutoCAD'),
            ('coring', 'Concrete coring'),
            ('vapour_probes', 'Vapour probes'),
            ('data_processing', 'Data processing'),
        ]

        parking = getattr(self, 'supp_parking', None)
        try:
            if parking is not None and parking != '' and float(parking) > 0:
                items.append(f"Parking = ${format_number(float(parking))}")
        except (ValueError, TypeError):
            pass

        for key, label in bool_fields:
            if bool(getattr(self, f'supp_{key}', False)):
                items.append(label)

        for key, label in hourly_fields:
            value = getattr(self, f'supp_{key}', None)
            try:
                hours = float(value)
            except (ValueError, TypeError):
                continue
            if hours > 0:
                items.append(f"{label} = {format_number(hours)}")
        return "; ".join(items)
    
    def format_materials(self):
        """Format materials (4 items: Pin Flags, Lathe 24", Lathe 48", KMs Driven).
        Only includes materials with a quantity greater than zero."""
        items = []
        mat_fields = [
            ('pin_flags', 'Pin flags'),
            ('lathe_24', 'Lathe 24"'),
            ('lathe_48', 'Lathe 48"'),
            ('kms', 'KMs driven'),
        ]
        for key, label in mat_fields:
            value = getattr(self, f'mat_{key}', None)
            try:
                if value is not None and value != '' and float(value) > 0:
                    items.append(f"{label} x{value}")
            except (ValueError, TypeError):
                pass
        return "; ".join(items)
    
    def format_property_type(self):
        """Format property type selection."""
        prop = getattr(self, 'property_type', None)
        if prop == 'Private':
            return "Private property"
        elif prop == 'Public':
            return "Public property"
        elif prop == 'Both':
            return "Public and private property"
        return ""
    
    def format_combined_report(self):
        """Generate the complete combined report text."""
        sections = []

        # Travel Notes
        travel = getattr(self, 'travel_notes', '')
        if travel:
            sections.append(f"TRAVEL NOTES:\r{travel}")
        
        # Site Conditions
        site_cond = getattr(self, 'site_conditions', '')
        if site_cond:
            sections.append(f"SITE CONDITIONS (Obstructions, inaccessible areas, changes to scope etc.):\r{site_cond}")
        
        # Utility sections, including forced output for mapped missing docs.
        for utility_key, _, _ in self.utilities.UTILITY_TYPES:
            utility = getattr(self.utilities, utility_key)
            section = self.format_utility_section_with_missing_docs(utility_key, utility)
            if section:
                sections.append(section)
        
        # Hydrovac recommendation
        hydrovac_section = self.hydrovac.format_section()
        if hydrovac_section:
            sections.append(hydrovac_section)
        
        # Recommendations (with missing docs and not-in-scope warnings)
        reco_section = self.format_recommendations()
        if reco_section:
            sections.append(reco_section)
        
        return "\r\r".join(sections)

    def get_report_pagination(self):
        """Split report text between main and continuation pages."""
        combined_full = self.format_combined_report()
        billing_full = self.format_billing_details()

        main_combined, combined_overflow = split_text_at_limit(
            combined_full, REPORT_MAIN_COMBINED_MAX_CHARS
        )
        main_billing, billing_overflow = split_text_at_limit(
            billing_full, REPORT_MAIN_BILLING_MAX_CHARS
        )

        # Continuation content order requested by user:
        # combined report overflow first, then billing overflow.
        overflow_sections = []
        if combined_overflow:
            overflow_sections.append(combined_overflow)
        if billing_overflow:
            overflow_sections.append(billing_overflow)
        overflow_text = "\r\r".join(overflow_sections)

        return {
            'main_combined': main_combined,
            'main_billing': main_billing,
            'cont_pages': split_into_pages(overflow_text, REPORT_CONT_PAGE_MAX_CHARS),
        }

    def get_report_cont_pages(self):
        """Return continuation-page text chunks in render order."""
        return self.get_report_pagination().get('cont_pages', [])

    def get_report_cont_fields(self, page_index):
        """Return fields for report continuation template."""
        pages = self.get_report_cont_pages()
        text = pages[page_index] if page_index < len(pages) else ''
        return {
            'quadra_job_number': getattr(self, 'quadra_job_number', ''),
            'combined_report_cont': text,
        }
    
    # ------------------------------------------------------------------
    # PDF template field-mapping methods (for fillable PDF export)
    # ------------------------------------------------------------------
    
    def get_cover_fields(self):
        """Return dict mapping PDF form field names to values for the cover page."""
        fields = {
            'client_company': getattr(self, 'client_company', ''),
            'quadra_job_number': getattr(self, 'quadra_job_number', ''),
            'technician_name': getattr(self, 'technician_name', ''),
            'site_visit_date': format_date(self.site_visit_date) if hasattr(self, 'site_visit_date') else '',
            'site_address': getattr(self, 'site_address', ''),
        }
        cover_val = _to_pdf_file_value(getattr(self, 'cover_photo', None), 'cover_photo')
        if cover_val:
            fields['cover_photo'] = cover_val
        return fields
    
    def get_report_fields(self):
        """Return dict mapping PDF form field names to values for the report page.
        
        The client_signature field is intentionally excluded — it is a digital
        signature field in the PDF that the client signs on the exported document.
        """
        pagination = self.get_report_pagination()
        fields = {
            'quadra_job_number': getattr(self, 'quadra_job_number', ''),
            'bc1_call_number': self.format_bc1_display(),
            'weather': getattr(self, 'weather', '') or '',
            'billing_details': pagination['main_billing'],
            'combined_report': pagination['main_combined'],
            'summary_text': (getattr(self, 'work_summary', '') or ''),
            'client_po_number': getattr(self, 'client_po_number', '') or '',
            'client_rep_name': getattr(self, 'client_rep_name', '') or '',
            'client_job_number': getattr(self, 'client_job_number', '') or '',
            'missing_other': getattr(self, 'missing_docs_other', '') or '',
        }
        # Missing docs checkboxes
        doc_keys = ['hydro', 'comm', 'gas', 'municipal', 'pipeline', 'asbuilts']
        for key in doc_keys:
            fields[f'missing_{key}'] = self.missing_docs.get(key, False)
        # 2-hour minimum (True if any technician has it)
        fields['two_hr_min'] = bool(self.job.get_combined_totals().get('two_hr_min', False))
        return fields
    
    def get_export_filename(self):
        """Return the export filename: YYYY-MM-DD Client_Company Site_Address QJN."""
        import re
        date_str = format_date(self.site_visit_date, format='yyyy-MM-dd') if hasattr(self, 'site_visit_date') else ''
        company = getattr(self, 'client_company', '') or ''
        address = getattr(self, 'site_address', '') or ''
        job_num = getattr(self, 'quadra_job_number', '') or ''
        # Clean each part: replace newlines/tabs with spaces, strip extra whitespace
        parts = [date_str, company.strip(), address.replace('\n', ' ').replace('\r', ' ').strip(), job_num.strip()]
        filename = ' '.join(p for p in parts if p)
        # Remove characters unsafe for filenames
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        # Collapse multiple spaces
        filename = re.sub(r'\s+', ' ', filename).strip()
        # Ensure filename is never empty; empty names can collapse to generic "file".
        if not filename:
            filename = date_str or 'locate-report'
        return filename + '.pdf'


# Helper functions

def format_number(n):
    """Format number: remove trailing zeros."""
    if n == 0:
        return "0"
    s = f"{round(n * 100) / 100:.2f}"
    s = s.rstrip('0').rstrip('.')
    return s


def format_time_12hr(time_val):
    """Format time to 12-hour format."""
    if not time_val:
        return ""
    
    if isinstance(time_val, str):
        # Try to parse string
        time_val = time_val.strip().lower()
        # Handle various formats
        try:
            if 'am' in time_val or 'pm' in time_val:
                # Already has am/pm
                return time_val
            # Try HH:MM format
            parts = time_val.replace(':', '').strip()
            if len(parts) <= 2:
                hour = int(parts)
                minute = 0
            else:
                hour = int(parts[:-2])
                minute = int(parts[-2:])
            
            if hour == 0 or hour == 24:
                return f"12:{minute:02d} am"
            elif hour < 12:
                return f"{hour}:{minute:02d} am"
            elif hour == 12:
                return f"12:{minute:02d} pm"
            else:
                return f"{hour - 12}:{minute:02d} pm"
        except (ValueError, IndexError, TypeError):
            return str(time_val)
    
    # Handle datetime.time AND datetime.datetime (including DADateTime from
    # datatype: time fields).  datetime.datetime is NOT a subclass of
    # datetime.time, so we check for the .hour attribute generically.
    if hasattr(time_val, 'hour') and hasattr(time_val, 'minute'):
        hour = time_val.hour
        minute = time_val.minute
        if hour == 0:
            return f"12:{minute:02d} am"
        elif hour < 12:
            return f"{hour}:{minute:02d} am"
        elif hour == 12:
            return f"12:{minute:02d} pm"
        else:
            return f"{hour - 12}:{minute:02d} pm"
    
    return str(time_val)


def oxford_join(items):
    """Join list with Oxford comma."""
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + ", and " + items[-1]


def format_totals_line(totals):
    """Format totals dict as 'EM = 3; GPR = 3.5; 2Hr Min = Yes; ...'."""
    parts = []
    labels = Technician.HOUR_LABELS
    for key in HOUR_TYPES_NUMERIC:
        value = totals.get(key, 0)
        if value and float(value) > 0:
            parts.append(f"{labels.get(key, key)} = {format_number(float(value))}")
    return "; ".join(parts)


def normalize_pdf_text(text):
    """Normalize line endings and trim whitespace for PDF field values."""
    return (text or '').replace('\n', '\r').strip()


def split_text_at_limit(text, max_chars):
    """Split text near max_chars, preferring natural breakpoints."""
    normalized = normalize_pdf_text(text)
    if not normalized:
        return '', ''
    if len(normalized) <= max_chars:
        return normalized, ''

    min_split = int(max_chars * 0.6)
    split_at = -1
    for token in ['\r\r', '\r', '; ', ' ']:
        idx = normalized.rfind(token, min_split, max_chars + 1)
        if idx >= min_split:
            split_at = idx + len(token)
            break
    if split_at < min_split:
        split_at = max_chars

    first = normalized[:split_at].rstrip()
    remainder = normalized[split_at:].lstrip()
    if not first:
        first = normalized[:max_chars].rstrip()
        remainder = normalized[max_chars:].lstrip()
    return first, remainder


def split_into_pages(text, max_chars):
    """Split text into multiple continuation-page chunks."""
    remaining = normalize_pdf_text(text)
    pages = []
    while remaining:
        page_text, overflow = split_text_at_limit(remaining, max_chars)
        if not page_text:
            break
        pages.append(page_text)
        remaining = overflow
    return pages


def _extract_file(file_val):
    """Extract a single DAFile from a DAFileList for PDF template image fields.

    Docassemble's ``datatype: file`` stores uploads as DAFileList.  PDF template
    image fields (pushbutton with 'Icon only' layout) need a single DAFile
    object.  This helper handles both DAFileList (returns first item) and plain
    DAFile (returns as-is).  Returns None if no valid file is found.
    """
    if file_val is None:
        return None
    # DAFileList or list-like → extract first item
    if hasattr(file_val, '__getitem__') and hasattr(file_val, '__len__'):
        try:
            if len(file_val) > 0:
                return file_val[0]
        except Exception:
            pass
        return None
    return file_val


def _to_pdf_file_value(file_val, field_name):
    """Return a PDF-friendly value for image fields.

    Prefers Docassemble's [FILE ...] markup string (produced by str(DAFile)).
    Falls back to returning the DAFile object if conversion fails.
    """
    file_obj = _extract_file(file_val)
    if not file_obj:
        return None
    try:
        rendered = str(file_obj)
    except Exception:
        return file_obj
    is_file_markup = isinstance(rendered, str) and rendered.startswith('[FILE ')
    if is_file_markup:
        return rendered
    return file_obj


HEADER_WIDTH = 18

def make_line(header, content):
    """Create aligned line with header and content."""
    if not content:
        return ""
    s = f"{header}:"
    while len(s) < HEADER_WIDTH:
        s += " "
    return s + content


def make_continuation_line(content):
    """Create continuation line (indented to align with content)."""
    if not content:
        return ""
    return " " * HEADER_WIDTH + content


def time_15min_choices():
    """Generate time choices in 15-minute increments for dropdown fields.

    Returns a list of dicts [{display_label: stored_value}, ...] suitable for
    Docassemble ``choices:`` on a field.  Stored values use 24-hour ``HH:MM``
    format (compatible with the existing ``format_time_12hr`` helper).
    """
    choices = []
    for hour in range(24):
        for minute in (0, 15, 30, 45):
            value = f"{hour:02d}:{minute:02d}"
            if hour == 0:
                display_hour = 12
                ampm = 'AM'
            elif hour < 12:
                display_hour = hour
                ampm = 'AM'
            elif hour == 12:
                display_hour = 12
                ampm = 'PM'
            else:
                display_hour = hour - 12
                ampm = 'PM'
            display = f"{display_hour}:{minute:02d} {ampm}"
            choices.append({display: value})
    return choices


# ============================================================
# PDF Archival — save finalized reports to server filesystem
# ============================================================

# Default archive directory inside the Docker container's persistent volume.
# This path is inside the da-data volume and survives container restarts.
REPORT_ARCHIVE_DIR = os.environ.get(
    'QUADRA_REPORT_ARCHIVE_DIR',
    '/usr/share/docassemble/files/reports'
)


class ReportArchiver:
    """Save and serve finalized PDF reports from the server filesystem."""

    @staticmethod
    def ensure_archive_dir():
        """Create the archive directory if it does not exist."""
        os.makedirs(REPORT_ARCHIVE_DIR, exist_ok=True)

    @staticmethod
    def archive_pdf(pdf_file, job_number):
        """Copy a generated PDF to the archive directory.

        Args:
            pdf_file: A Docassemble DAFile or file-like object with a .path() method.
            job_number: The Quadra job number (used as the filename).

        Returns:
            The full path of the archived file, or None on failure.
        """
        import re
        import shutil
        try:
            ReportArchiver.ensure_archive_dir()
            # Sanitize job number for use as filename
            safe_name = re.sub(r'[<>:"/\\|?*]', '', str(job_number)).strip()
            if not safe_name:
                safe_name = 'unknown'
            dest = os.path.join(REPORT_ARCHIVE_DIR, safe_name + '.pdf')
            # Get source path — works for DAFile objects
            if hasattr(pdf_file, 'path'):
                src = pdf_file.path()
            elif isinstance(pdf_file, str):
                src = pdf_file
            else:
                log.warning("ReportArchiver: cannot determine source path for %s", type(pdf_file))
                return None
            shutil.copy2(src, dest)
            log.info("ReportArchiver: archived %s -> %s", src, dest)
            return dest
        except Exception as e:
            log.error("ReportArchiver: failed to archive PDF for job %s: %s", job_number, e)
            return None

    @staticmethod
    def get_archived_path(job_number):
        """Return the full path of an archived PDF, or None if it doesn't exist."""
        import re
        safe_name = re.sub(r'[<>:"/\\|?*]', '', str(job_number)).strip()
        if not safe_name:
            return None
        path = os.path.join(REPORT_ARCHIVE_DIR, safe_name + '.pdf')
        return path if os.path.isfile(path) else None

    @staticmethod
    def list_archived():
        """Return a list of (job_number, file_path) tuples for all archived PDFs."""
        ReportArchiver.ensure_archive_dir()
        results = []
        for fname in os.listdir(REPORT_ARCHIVE_DIR):
            if fname.lower().endswith('.pdf'):
                job_num = fname[:-4]  # strip .pdf
                results.append((job_num, os.path.join(REPORT_ARCHIVE_DIR, fname)))
        return results


# ============================================================
# Dropbox Integration — OAuth2 + file upload
# ============================================================

class DropboxService:
    """Manage Dropbox OAuth2 authentication and file uploads.

    Tokens are stored per-user in Docassemble's DAStore (persistent
    key-value storage that survives across sessions).

    Configuration:
        Set these in Docassemble config.yml or as environment variables:
        - DROPBOX_APP_KEY: Your Dropbox app key
        - DROPBOX_APP_SECRET: Your Dropbox app secret (for confidential apps)
    """

    STORE_KEY = 'dropbox_refresh_token'

    @staticmethod
    def _get_app_key():
        """Get the Dropbox app key from config or environment."""
        from docassemble.base.util import get_config
        key = get_config('dropbox app key')
        if not key:
            key = os.environ.get('DROPBOX_APP_KEY', '')
        return key or ''

    @staticmethod
    def _get_app_secret():
        """Get the Dropbox app secret from config or environment."""
        from docassemble.base.util import get_config
        secret = get_config('dropbox app secret')
        if not secret:
            secret = os.environ.get('DROPBOX_APP_SECRET', '')
        return secret or ''

    @staticmethod
    def is_configured():
        """Check if Dropbox app credentials are configured."""
        return bool(DropboxService._get_app_key())

    @staticmethod
    def get_auth_url(redirect_uri):
        """Generate a Dropbox OAuth2 authorization URL.

        Args:
            redirect_uri: The callback URL that Dropbox will redirect to.

        Returns:
            (auth_url, csrf_token) tuple, or (None, None) if not configured.
        """
        try:
            import dropbox
        except ImportError:
            log.error("DropboxService: dropbox package not installed")
            return None, None

        app_key = DropboxService._get_app_key()
        app_secret = DropboxService._get_app_secret()
        if not app_key:
            return None, None

        auth_flow = dropbox.DropboxOAuth2Flow(
            consumer_key=app_key,
            consumer_secret=app_secret,
            redirect_uri=redirect_uri,
            session={},  # We manage state ourselves
            csrf_token_session_key='dropbox-auth-csrf-token',
            token_access_type='offline',
        )
        auth_url = auth_flow.start()
        csrf_token = auth_flow.session.get('dropbox-auth-csrf-token', '')
        return auth_url, csrf_token

    @staticmethod
    def complete_auth(auth_code):
        """Exchange an authorization code for a refresh token.

        Args:
            auth_code: The authorization code from Dropbox callback.

        Returns:
            True if authentication succeeded and token was stored, False otherwise.
        """
        try:
            import dropbox
        except ImportError:
            log.error("DropboxService: dropbox package not installed")
            return False

        app_key = DropboxService._get_app_key()
        app_secret = DropboxService._get_app_secret()
        if not app_key:
            return False

        try:
            from dropbox import DropboxOAuth2FlowNoRedirect
            flow = DropboxOAuth2FlowNoRedirect(
                consumer_key=app_key,
                consumer_secret=app_secret,
                token_access_type='offline',
            )
            result = flow.finish(auth_code)

            # Store refresh token
            from docassemble.base.util import DAStore
            store = DAStore()
            store.set(DropboxService.STORE_KEY, {
                'refresh_token': result.refresh_token,
                'account_id': result.account_id,
            })
            log.info("DropboxService: auth completed for account %s", result.account_id)
            return True
        except Exception as e:
            log.error("DropboxService: auth failed: %s", e)
            return False

    @staticmethod
    def is_linked():
        """Check if the current user has a linked Dropbox account."""
        try:
            from docassemble.base.util import DAStore
            store = DAStore()
            data = store.get(DropboxService.STORE_KEY)
            return bool(data and data.get('refresh_token'))
        except Exception:
            return False

    @staticmethod
    def unlink():
        """Remove the stored Dropbox token for the current user."""
        try:
            from docassemble.base.util import DAStore
            store = DAStore()
            store.delete(DropboxService.STORE_KEY)
            return True
        except Exception as e:
            log.error("DropboxService: unlink failed: %s", e)
            return False

    @staticmethod
    def upload_file(local_path, dropbox_path):
        """Upload a file to the user's Dropbox.

        Args:
            local_path: Path to the local file to upload.
            dropbox_path: The destination path in Dropbox (e.g., '/Reports/report.pdf').

        Returns:
            True if upload succeeded, False otherwise.
        """
        try:
            import dropbox
        except ImportError:
            log.error("DropboxService: dropbox package not installed")
            return False

        try:
            from docassemble.base.util import DAStore
            store = DAStore()
            data = store.get(DropboxService.STORE_KEY)
            if not data or not data.get('refresh_token'):
                log.error("DropboxService: no refresh token stored")
                return False

            dbx = dropbox.Dropbox(
                app_key=DropboxService._get_app_key(),
                app_secret=DropboxService._get_app_secret(),
                oauth2_refresh_token=data['refresh_token'],
            )

            # Get source file path
            if hasattr(local_path, 'path'):
                src = local_path.path()
            elif isinstance(local_path, str):
                src = local_path
            else:
                log.error("DropboxService: cannot determine file path from %s", type(local_path))
                return False

            # Ensure dropbox_path starts with /
            if not dropbox_path.startswith('/'):
                dropbox_path = '/' + dropbox_path

            with open(src, 'rb') as f:
                dbx.files_upload(
                    f.read(),
                    dropbox_path,
                    mode=dropbox.files.WriteMode.overwrite,
                )
            log.info("DropboxService: uploaded %s to %s", src, dropbox_path)
            return True
        except Exception as e:
            log.error("DropboxService: upload failed: %s", e)
            return False


# ============================================================
# Job Map — geocoding + persistent pin storage
# ============================================================

class JobMapService:
    """Manage geocoded job pins for the interactive map.

    Uses Docassemble's write_record/read_records for persistent storage
    and geopy's Nominatim geocoder (free, no API key needed).
    """

    RECORD_KEY = 'job_map_pins'

    @staticmethod
    def geocode_address(address_str):
        """Geocode an address string to (latitude, longitude).

        Uses Nominatim (OpenStreetMap) via geopy. Free, no API key needed.
        Rate limit: 1 request/second (enforced by geopy's default timeout).

        Args:
            address_str: The site address to geocode.

        Returns:
            (lat, lng) tuple, or (None, None) if geocoding fails.
        """
        try:
            from geopy.geocoders import Nominatim
            geolocator = Nominatim(user_agent='quadra-locate-report/1.0')
            # Clean up the address for better geocoding
            clean_addr = address_str.replace('\n', ', ').replace('\r', ', ').strip()
            # Append BC, Canada if not already present (most jobs are in BC)
            if 'canada' not in clean_addr.lower() and 'bc' not in clean_addr.lower():
                clean_addr += ', BC, Canada'
            location = geolocator.geocode(clean_addr, timeout=10)
            if location:
                return (location.latitude, location.longitude)
            log.warning("JobMapService: geocoding returned no results for '%s'", clean_addr)
            return (None, None)
        except Exception as e:
            log.error("JobMapService: geocoding failed for '%s': %s", address_str, e)
            return (None, None)

    @staticmethod
    def pin_exists(job_number):
        """Check if a pin already exists for this job number."""
        from docassemble.base.util import read_records
        for _rid, data in read_records(JobMapService.RECORD_KEY).items():
            if isinstance(data, dict) and data.get('job_number') == str(job_number):
                return True
        return False

    @staticmethod
    def save_job_pin(report):
        """Geocode the report's address and save a map pin.

        Only creates a new pin if the job number is unique.
        Skips silently on geocoding failure.

        Args:
            report: A LocateReport object with quadra_job_number, site_address,
                    client_company, and site_visit_date attributes.

        Returns:
            True if pin was saved, False otherwise.
        """
        from docassemble.base.util import write_record, read_records, delete_record, \
            format_date as da_format_date

        job_number = str(getattr(report, 'quadra_job_number', ''))
        if not job_number:
            return False

        address = str(getattr(report, 'site_address', ''))
        if not address:
            return False

        # Check for existing pin — update if found, create if new
        existing_rid = None
        for rid, data in read_records(JobMapService.RECORD_KEY).items():
            if isinstance(data, dict) and data.get('job_number') == job_number:
                existing_rid = rid
                break

        lat, lng = JobMapService.geocode_address(address)
        if lat is None or lng is None:
            log.warning("JobMapService: skipping pin for job %s (geocoding failed)", job_number)
            return False

        pin_data = {
            'job_number': job_number,
            'site_address': address.replace('\n', ', ').replace('\r', ', ').strip(),
            'client_company': str(getattr(report, 'client_company', '')),
            'site_visit_date': da_format_date(report.site_visit_date, format='yyyy-MM-dd') if hasattr(report, 'site_visit_date') else '',
            'lat': lat,
            'lng': lng,
            'pdf_filename': job_number + '.pdf',
            'created_at': datetime.now().isoformat(),
        }

        if existing_rid is not None:
            delete_record(JobMapService.RECORD_KEY, existing_rid)

        write_record(JobMapService.RECORD_KEY, pin_data)
        log.info("JobMapService: saved pin for job %s at (%s, %s)", job_number, lat, lng)
        return True

    @staticmethod
    def get_all_pins():
        """Return all job map pins as a list of dicts.

        Returns:
            List of pin dicts with keys: job_number, site_address, client_company,
            site_visit_date, lat, lng, pdf_filename.
        """
        from docassemble.base.util import read_records
        pins = []
        for _rid, data in read_records(JobMapService.RECORD_KEY).items():
            if isinstance(data, dict) and data.get('lat') is not None:
                pins.append(data)
        return pins
