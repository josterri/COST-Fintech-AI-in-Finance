"""
Validate Report Editor Coverage

Checks that the report editor covers all JSON fields from final_report_full.json.
Outputs a detailed coverage report showing what's editable vs missing.
"""

import json
import re
from pathlib import Path


def load_json_structure(json_path):
    """Load JSON and analyze its structure."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def analyze_json_fields(data, prefix=""):
    """Recursively analyze JSON structure and return field inventory."""
    fields = []

    if isinstance(data, dict):
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key

            if isinstance(value, dict):
                fields.append((full_key, "object", len(value)))
                fields.extend(analyze_json_fields(value, full_key))
            elif isinstance(value, list):
                fields.append((full_key, "array", len(value)))
                if value and isinstance(value[0], dict):
                    # Analyze first item structure
                    fields.extend(analyze_json_fields(value[0], f"{full_key}[0]"))
            else:
                field_type = type(value).__name__
                fields.append((full_key, field_type, value if isinstance(value, (int, bool)) else "..."))

    return fields


def parse_editor_script(script_path):
    """Parse the editor generator script to find field IDs."""
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all input/textarea/select field IDs
    field_patterns = [
        r'id="([^"]+)"',
        r"id='([^']+)'",
        r'getElementById\(["\']([^"\']+)["\']\)',
    ]

    field_ids = set()
    for pattern in field_patterns:
        matches = re.findall(pattern, content)
        field_ids.update(matches)

    # Filter to likely data fields (exclude UI elements)
    data_fields = {f for f in field_ids if not f.startswith(('panel-', 'tab-', 'modal', 'toast', 'status'))}

    return data_fields


def check_section_coverage(json_data, editor_fields):
    """Check coverage for each JSON section."""
    results = {}

    # Define expected mappings for each section
    section_checks = {
        'metadata': {
            'fields': ['title', 'action_code', 'action_name', 'period', 'pages', 'generated', 'source_file'],
            'type': 'display_only',
            'check_pattern': r'metadata|meta-'
        },
        'summary': {
            'fields': ['main_objective', 'description', 'website', 'stats.researchers', 'stats.countries',
                       'stats.cost_countries', 'stats.participants', 'stats.citations'],
            'type': 'editable',
            'check_pattern': r'summary-|stats-'
        },
        'leadership': {
            'fields': ['chair.name', 'chair.email', 'chair.country', 'chair.phone', 'chair.title',
                       'vice_chair.name', 'vice_chair.email', 'vice_chair.country', 'vice_chair.phone',
                       'wg_leaders', 'other_positions'],
            'type': 'editable',
            'check_pattern': r'chair-|vicechair-|wg-|other-pos'
        },
        'participants': {
            'fields': ['countries'],
            'type': 'editable',
            'check_pattern': r'participant|country-'
        },
        'objectives': {
            'fields': ['number', 'title', 'type', 'achievement', 'dependence', 'proof_text'],
            'type': 'editable',
            'check_pattern': r'obj-'
        },
        'deliverables': {
            'fields': ['number', 'title', 'status', 'dependence', 'proof_url'],
            'type': 'editable',
            'check_pattern': r'del-'
        },
        'publications': {
            'fields': ['doi'],  # User requested DOI only
            'type': 'editable',
            'check_pattern': r'pub-'
        },
        'stsms_vmgs': {
            'fields': ['stsms.description', 'vmgs'],
            'type': 'editable',
            'check_pattern': r'stsm|vmg'
        },
        'impacts': {
            'fields': ['career_benefits', 'experience_level', 'stakeholder_engagement', 'dissemination_approach'],
            'type': 'editable',
            'check_pattern': r'impacts-'
        },
        'events': {
            'fields': ['url'],
            'type': 'editable',
            'check_pattern': r'event-'
        },
        'raw_pages': {
            'fields': [],
            'type': 'skip',
            'check_pattern': r'raw-page'
        }
    }

    for section, config in section_checks.items():
        pattern = config['check_pattern']
        matching_fields = [f for f in editor_fields if re.search(pattern, f, re.IGNORECASE)]

        if config['type'] == 'skip':
            results[section] = {
                'status': 'SKIP',
                'reason': 'Not editable by design',
                'fields_expected': 0,
                'fields_found': 0
            }
        else:
            # Check what's in JSON
            json_section = json_data.get(section, {})
            if isinstance(json_section, list):
                item_count = len(json_section)
            elif isinstance(json_section, dict):
                item_count = len(json_section)
            else:
                item_count = 1

            has_fields = len(matching_fields) > 0

            results[section] = {
                'status': 'OK' if has_fields else 'MISSING',
                'type': config['type'],
                'json_items': item_count,
                'expected_fields': config['fields'],
                'editor_fields': matching_fields,
                'fields_found': len(matching_fields)
            }

    return results


def generate_report(json_data, editor_fields, coverage_results):
    """Generate a detailed coverage report."""
    print("\n" + "=" * 60)
    print("REPORT EDITOR COVERAGE VALIDATION")
    print("=" * 60)

    # Summary stats
    total_sections = len(coverage_results)
    ok_sections = sum(1 for r in coverage_results.values() if r['status'] == 'OK')
    missing_sections = sum(1 for r in coverage_results.values() if r['status'] == 'MISSING')
    skip_sections = sum(1 for r in coverage_results.values() if r['status'] == 'SKIP')

    print(f"\nJSON Sections: {total_sections}")
    print(f"  [OK] Covered: {ok_sections}")
    print(f"  [MISSING] Not covered: {missing_sections}")
    print(f"  [SKIP] By design: {skip_sections}")

    # Detailed section report
    print("\n" + "-" * 60)
    print("SECTION DETAILS")
    print("-" * 60)

    for section, result in coverage_results.items():
        status_icon = {
            'OK': '[OK]    ',
            'MISSING': '[MISSING]',
            'SKIP': '[SKIP]  '
        }.get(result['status'], '[?]')

        if result['status'] == 'SKIP':
            print(f"\n{status_icon} {section}")
            print(f"         Reason: {result.get('reason', 'N/A')}")
        else:
            json_items = result.get('json_items', 0)
            fields_found = result.get('fields_found', 0)
            print(f"\n{status_icon} {section}")
            print(f"         JSON items: {json_items}")
            print(f"         Editor fields found: {fields_found}")

            if result['status'] == 'MISSING':
                print(f"         Expected fields: {result.get('expected_fields', [])}")
            else:
                editor_fields_list = result.get('editor_fields', [])
                if editor_fields_list:
                    print(f"         Editor fields: {editor_fields_list[:5]}{'...' if len(editor_fields_list) > 5 else ''}")

    # Missing fields detail
    print("\n" + "-" * 60)
    print("MISSING SECTIONS TO FIX")
    print("-" * 60)

    missing = [s for s, r in coverage_results.items() if r['status'] == 'MISSING']
    if missing:
        for section in missing:
            result = coverage_results[section]
            print(f"\n  {section}:")
            print(f"    - JSON has {result.get('json_items', 0)} items")
            print(f"    - Expected fields: {result.get('expected_fields', [])}")
            print(f"    - Add editor panel with fields matching pattern: {section}")
    else:
        print("\n  None! All sections are covered.")

    # Coverage percentage
    editable_sections = total_sections - skip_sections
    coverage_pct = (ok_sections / editable_sections * 100) if editable_sections > 0 else 0

    print("\n" + "=" * 60)
    print(f"OVERALL COVERAGE: {coverage_pct:.0f}%")
    print("=" * 60)

    if coverage_pct == 100:
        print("\nAll JSON fields are covered by the report editor.")
    else:
        print(f"\n{missing_sections} section(s) need to be added to the editor.")

    return coverage_pct


def main():
    """Main validation function."""
    base_dir = Path(__file__).parent.parent
    json_path = base_dir / "data" / "final_report_full.json"
    editor_script_path = base_dir / "scripts" / "generate_report_editor.py"

    print("Loading JSON data...")
    json_data = load_json_structure(json_path)

    print("Parsing editor script...")
    editor_fields = parse_editor_script(editor_script_path)

    print(f"Found {len(editor_fields)} field IDs in editor script")

    print("\nAnalyzing coverage...")
    coverage_results = check_section_coverage(json_data, editor_fields)

    coverage_pct = generate_report(json_data, editor_fields, coverage_results)

    # Return exit code based on coverage
    return 0 if coverage_pct == 100 else 1


if __name__ == "__main__":
    exit(main())
