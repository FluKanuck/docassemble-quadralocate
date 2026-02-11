"""
Custom Python objects for Quadra Utility Locate Report
"""
from docassemble.base.util import DAObject, DAList, DADict, format_time, format_date
from datetime import datetime, time


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
        for hour_type in self.HOUR_TYPES:
            value = self.hours.get(hour_type)
            if hour_type == 'two_hr_min':
                if value:
                    parts.append(f"{self.HOUR_LABELS.get(hour_type, hour_type)} = Yes")
            elif value and float(value) > 0:
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
            photo = _extract_file(raw)
            if photo:
                # Docassemble only places images into /Sig (signature) fields—not /Btn (push button).
                # Pass [FILE ref] format so the filler routes to images. PDF template must use Signature fields.
                ref = photo._get_unqualified_reference()
                fields[f'photo_{n}'] = '[FILE ' + ref + ']'
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
    
    def get_drawing_fields(self, job_number=''):
        """Return dict mapping PDF form field names to values for this drawing."""
        fields = {
            'quadra_job_number': str(job_number),
            'drawing_title': getattr(self, 'title', '') or '',
        }
        drawing_file = _extract_file(getattr(self, 'file', None))
        if drawing_file:
            fields['drawing_image'] = '[FILE ' + drawing_file._get_unqualified_reference() + ']'
        return fields


class LocateReport(DAObject):
    """Main report object that aggregates all components."""
    
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
        doc_labels = {
            'hydro': 'BC Hydro',
            'comm': 'Communications',
            'gas': 'Fortis',
            'municipal': 'Municipal',
            'pipeline': 'Pipeline',
            'asbuilts': 'As-builts'
        }
        
        for key, label in doc_labels.items():
            if self.missing_docs.get(key, False):
                missing.append(label)
        
        if not missing:
            return ""
        
        docs_list = oxford_join(missing)
        return (f"{docs_list} documentation missing on site. It is the responsibility "
                "of the Ground Disturber, prior to ground disturbance, to obtain and "
                "review said documentation.")
    
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
        """Format supplemental charges (9 items: Parking $ + 8 yes/no)."""
        items = []
        supp_fields = [
            ('parking', 'Parking'),
            ('traffic_control', 'Traffic control'),
            ('permitting', 'Permitting'),
            ('loa', 'LOA'),
            ('desktop', 'Desktop review'),
            ('cad', 'AutoCAD'),
            ('coring', 'Concrete coring'),
            ('vapour_probes', 'Vapour probes'),
            ('data_processing', 'Data processing'),
        ]
        for key, label in supp_fields:
            value = getattr(self, f'supp_{key}', None)
            if value:
                items.append(f"{label} = {value}")
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
        
        # Summary of Work (user-entered overview, first in report)
        work_summary = getattr(self, 'work_summary', '') or ''
        if work_summary:
            sections.append(f"SUMMARY OF WORK PERFORMED:\r{work_summary}")
        
        # Travel Notes
        travel = getattr(self, 'travel_notes', '')
        if travel:
            sections.append(f"TRAVEL NOTES:\r{travel}")
        
        # Site Conditions
        site_cond = getattr(self, 'site_conditions', '')
        if site_cond:
            sections.append(f"SITE CONDITIONS (Obstructions, inaccessible areas, changes to scope etc.):\r{site_cond}")
        
        # Utility sections (storm and sanitary now have individual summaries)
        for utility in self.utilities.get_active_utilities():
            section = utility.format_section()
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
        cover = _extract_file(getattr(self, 'cover_photo', None))
        if cover:
            fields['cover_photo'] = '[FILE ' + cover._get_unqualified_reference() + ']'
        return fields
    
    def get_report_fields(self):
        """Return dict mapping PDF form field names to values for the report page.
        
        The client_signature field is intentionally excluded — it is a digital
        signature field in the PDF that the client signs on the exported document.
        """
        combined = self.format_combined_report()
        fields = {
            'quadra_job_number': getattr(self, 'quadra_job_number', ''),
            'bc1_call_number': self.format_bc1_display(),
            'weather': getattr(self, 'weather', '') or '',
            'billing_details': self.format_billing_details(),
            'combined_report': combined,
            'summary_text': combined,  # PDF template may use either field name
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
    for key in Technician.HOUR_TYPES:
        value = totals.get(key, 0)
        if key == 'two_hr_min':
            if value:
                parts.append(f"{labels.get(key, key)} = Yes")
        elif value and float(value) > 0:
            parts.append(f"{labels.get(key, key)} = {format_number(float(value))}")
    return "; ".join(parts)


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
