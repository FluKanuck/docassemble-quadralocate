"""
Custom Python objects for Quadra Utility Locate Report
"""
from docassemble.base.util import DAObject, DAList, DADict, format_time, format_date
from datetime import datetime, time

__all__ = [
    'UtilityType',
    'UtilityMatrix',
    'Technician',
    'WorkDay',
    'MultiDayJob',
    'HydrovacRecommendation',
    'PhotoPage',
    'Drawing',
    'LocateReport'
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
    
    def should_display(self):
        """Determine if this utility section should appear in report."""
        return self.has_any_method() or (hasattr(self, 'summary') and self.summary)
    
    def get_method_labels(self):
        """Get list of human-readable method labels for selected methods."""
        labels = []
        method_label_map = {
            'em': 'Located with EM',
            'gpr': 'Located with GPR',
            'visual': 'Located visually',
            'not_located': 'Not located',
            'not_in_area': 'Not in proposed work area'
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
        ('electrical', 'Electrical', ['em', 'gpr', 'visual', 'not_located', 'not_in_area']),
        ('communications', 'Communications', ['em', 'gpr', 'visual', 'not_located', 'not_in_area']),
        ('gas', 'Gas / Pipeline', ['em', 'gpr', 'visual', 'not_located', 'not_in_area']),
        ('water', 'Water', ['em', 'gpr', 'visual', 'not_located', 'not_in_area']),
        ('storm', 'Storm', ['em', 'gpr', 'visual', 'not_located', 'not_in_area']),
        ('sanitary', 'Sanitary', ['em', 'gpr', 'visual', 'not_located', 'not_in_area']),
        ('ditch', 'Ditch', ['visual', 'not_located']),  # Limited methods
        ('unknown', 'Unknown / Other', ['em', 'gpr', 'visual', 'not_located', 'not_in_area']),
    ]
    
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        # Initialize each utility type
        for key, display_name, methods in self.UTILITY_TYPES:
            utility = UtilityType()
            utility.key = key
            utility.display_name = display_name
            utility.available_methods = methods
            setattr(self, key, utility)
    
    def get_active_utilities(self):
        """Return list of utilities that should appear in report."""
        active = []
        for key, _, _ in self.UTILITY_TYPES:
            utility = getattr(self, key)
            if utility.should_display():
                active.append(utility)
        return active


class Technician(DAObject):
    """Represents a technician with their hours breakdown."""
    
    HOUR_TYPES = ['em', 'gpr', 'travel', 'survey', 'concrete_gpr', 'standby']
    HOUR_LABELS = {
        'em': 'EM',
        'gpr': 'GPR',
        'travel': 'Travel',
        'survey': 'Survey',
        'concrete_gpr': 'Conc. GPR',
        'standby': 'Standby'
    }
    
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        self.initializeAttribute('hours', DADict)
        for hour_type in self.HOUR_TYPES:
            if hour_type not in self.hours:
                self.hours[hour_type] = 0
    
    def has_any_hours(self):
        """Check if technician has any hours recorded."""
        for hour_type in self.HOUR_TYPES:
            if self.hours.get(hour_type, 0) > 0:
                return True
        return False
    
    def get_total_hours(self):
        """Calculate total hours for this technician."""
        total = 0
        for hour_type in self.HOUR_TYPES:
            total += float(self.hours.get(hour_type, 0) or 0)
        return total
    
    def format_hours_line(self):
        """Format hours as 'EM = 2; GPR = 1.5; Travel = 0.5'."""
        parts = []
        for hour_type in self.HOUR_TYPES:
            value = self.hours.get(hour_type, 0)
            if value and float(value) > 0:
                label = self.HOUR_LABELS.get(hour_type, hour_type)
                # Format number: remove trailing zeros
                formatted = format_number(float(value))
                parts.append(f"{label} = {formatted}")
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
        self.initializeAttribute('technicians', DAList.using(object_type=Technician, there_are_any=True))
    
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
        """Sum all technician hours by type for this day."""
        totals = {ht: 0 for ht in Technician.HOUR_TYPES}
        for tech in self.technicians:
            for hour_type in Technician.HOUR_TYPES:
                totals[hour_type] += float(tech.hours.get(hour_type, 0) or 0)
        return totals


class MultiDayJob(DAObject):
    """Manages multi-day job with multiple work days."""
    
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        self.initializeAttribute('work_days', DAList.using(object_type=WorkDay, there_are_any=True))
        self.is_multi_day = False
    
    def get_all_technicians(self):
        """Get unique list of all technicians across all days."""
        tech_dict = {}
        for day in self.work_days:
            for tech in day.technicians:
                name = getattr(tech, 'name', 'Unknown')
                if name not in tech_dict:
                    tech_dict[name] = {'hours': {ht: 0 for ht in Technician.HOUR_TYPES}}
                for hour_type in Technician.HOUR_TYPES:
                    tech_dict[name]['hours'][hour_type] += float(tech.hours.get(hour_type, 0) or 0)
        return tech_dict
    
    def get_combined_totals(self):
        """Get combined hour totals across all days and technicians."""
        totals = {ht: 0 for ht in Technician.HOUR_TYPES}
        for day in self.work_days:
            day_totals = day.get_all_hours_by_type()
            for hour_type in Technician.HOUR_TYPES:
                totals[hour_type] += day_totals[hour_type]
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
            for day in self.work_days:
                date_str = format_date(day.date, format='short') if hasattr(day, 'date') else 'Unknown'
                tech_parts = []
                for tech in day.technicians:
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
        self.recommended = False
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
    """Represents a page of photos in the report."""
    
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        self.page_number = 1
        self.photos = None
        self.comments = ""
    
    def has_content(self):
        """Check if this page has any photos or comments."""
        return (self.photos and len(self.photos) > 0) or self.comments


class Drawing(DAObject):
    """Represents a locate drawing with format specification."""
    
    FORMAT_NORMAL = 'normal'
    FORMAT_LARGE = 'large'
    
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        self.page_number = 1
        self.format = self.FORMAT_NORMAL
        self.file = None
        self.title = ""
    
    def is_large_format(self):
        """Check if this is a large format drawing."""
        return self.format == self.FORMAT_LARGE
    
    def get_format_label(self):
        """Get human-readable format label."""
        if self.format == self.FORMAT_LARGE:
            return "Large Format (11x17)"
        return "Normal (Letter/A4)"


class LocateReport(DAObject):
    """Main report object that aggregates all components."""
    
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        self.initializeAttribute('utilities', UtilityMatrix)
        self.initializeAttribute('job', MultiDayJob)
        self.initializeAttribute('hydrovac', HydrovacRecommendation)
        self.initializeAttribute('missing_docs', DADict)
        self.initializeAttribute('photo_pages', DAList.using(object_type=PhotoPage))
        self.initializeAttribute('drawings', DAList.using(object_type=Drawing))
        self.num_photo_pages = 1
        self.num_drawings = 1
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
        """Format recommendations with auto-appended missing docs."""
        reco = getattr(self, 'recommendations', '') or ''
        missing_sentence = self.format_missing_docs_sentence()
        
        if missing_sentence:
            if reco:
                reco = f"{reco}\r\r{missing_sentence}"
            else:
                reco = missing_sentence
        
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
        """Format supplemental charges."""
        items = []
        supp_fields = [
            ('parking', 'Parking'),
            ('traffic_control', 'Traffic control'),
            ('permits', 'Permitting'),
            ('desktop', 'Desktop review'),
            ('cad', 'AutoCAD'),
            ('coring', 'Coring'),
            ('vapour_probes', 'Vapour probes'),
            ('camera', 'Camera inspection'),
            ('data_processing', 'Data processing'),
            ('orientation', 'Orientation Time'),
            ('sketch', 'Report Drafting'),
            ('kms', 'Kilometres'),
            ('loa', 'LOA'),
        ]
        
        for key, label in supp_fields:
            value = getattr(self, f'supp_{key}', None)
            if value:
                items.append(f"{label} = {value}")
        
        return "; ".join(items)
    
    def format_materials(self):
        """Format materials with 'x' prefix."""
        items = []
        mat_fields = [
            ('pin_flags', 'Pin flags'),
            ('lathe_24', 'Lathe 24"'),
            ('lathe_48', 'Lathe 48"'),
        ]
        
        for key, label in mat_fields:
            value = getattr(self, f'mat_{key}', None)
            if value:
                items.append(f"{label} x{value}")
        
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
        
        # Travel Notes (first)
        travel = getattr(self, 'travel_notes', '')
        if travel:
            sections.append(f"TRAVEL NOTES:\r{travel}")
        
        # Site Conditions
        site_cond = getattr(self, 'site_conditions', '')
        if site_cond:
            sections.append(f"SITE CONDITIONS (Obstructions, inaccessible areas, changes to scope etc.):\r{site_cond}")
        
        # Utility sections
        for utility in self.utilities.get_active_utilities():
            section = utility.format_section()
            if section:
                sections.append(section)
        
        # Storm and Sanitary combined (special handling)
        # Already handled in utilities
        
        # Hydrovac recommendation
        hydrovac_section = self.hydrovac.format_section()
        if hydrovac_section:
            sections.append(hydrovac_section)
        
        # Recommendations (with missing docs)
        reco_section = self.format_recommendations()
        if reco_section:
            sections.append(reco_section)
        
        return "\r\r".join(sections)


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
        except:
            return time_val
    
    if isinstance(time_val, time):
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
    """Format totals dict as 'EM = 3; GPR = 3.5; Travel = 0.5'."""
    parts = []
    order = ['em', 'gpr', 'travel', 'survey', 'concrete_gpr', 'standby']
    labels = Technician.HOUR_LABELS
    
    for key in order:
        value = totals.get(key, 0)
        if value > 0:
            label = labels.get(key, key)
            parts.append(f"{label} = {format_number(value)}")
    
    return "; ".join(parts)


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
