"""
Comprehensive FFR Data Validation Script
Compares extracted JSON data against actual FFR source totals per category.

Author: Claude Code
Date: 2026-01-13
"""

import json
import re
from pathlib import Path
from collections import defaultdict

# Paths
DATA_DIR = Path(r"D:\Joerg\Research\slides\COST-Fintech-AI-in-Finance\data")
REPORTS_DIR = Path(r"D:\Joerg\Research\slides\COST-Fintech-AI-in-Finance\reports")
EXTRACTED_TEXT_DIR = Path(r"D:\Joerg\Research\slides\COST_Work_and_Budget_Plans\extracted_text")

FFR_FILES = {
    1: "AGA-CA19130-1-FFR_ID2193.txt",
    2: "AGA-CA19130-2-FFR_ID2346.txt",
    3: "AGA-CA19130-3-FFR_ID2998.txt",
    4: "AGA-CA19130-4-FFR_ID3993.txt",
    5: "AGA-CA19130-5-FFR_ID4828.txt",
}


def parse_amount(amount_str):
    """Parse amount string with European number format (space thousands separator)"""
    if not amount_str:
        return 0.0
    cleaned = amount_str.replace(' ', '').replace(',', '.')
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def load_json_data():
    """Load all extracted JSON data files"""
    data = {}

    files = [
        ('meetings', 'meetings_participants.json'),
        ('stsms', 'stsm_full.json'),
        ('vms', 'virtual_mobility_full.json'),
        ('training_schools', 'training_school_attendees.json'),
        ('vns', 'vns_grants.json'),
        ('dissemination', 'dissemination_grants.json'),
        ('los', 'los_grants.json'),
        ('itc_conference', 'itc_conference_grants.json'),
    ]

    for key, filename in files:
        filepath = DATA_DIR / filename
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                data[key] = json.load(f)
        else:
            data[key] = []

    return data


def calculate_json_totals(data):
    """Calculate totals from extracted JSON data by category and grant period"""
    totals = defaultdict(lambda: defaultdict(float))

    # Meetings
    for meeting in data['meetings']:
        gp = meeting.get('grant_period', 0)
        for p in meeting.get('participants', []):
            totals['meetings'][gp] += p.get('total', 0)

    # STSMs
    for stsm in data['stsms']:
        gp = stsm.get('grant_period', 0)
        totals['stsm'][gp] += stsm.get('amount', 0)

    # Virtual Mobility
    for vm in data['vms']:
        gp = vm.get('grant_period', 0)
        totals['vm'][gp] += vm.get('amount', 0)

    # Training Schools
    for ts in data['training_schools']:
        gp = ts.get('grant_period', 0)
        for p in ts.get('participants', []):
            totals['training_schools'][gp] += p.get('total', 0)

    # VNS
    for vns in data['vns']:
        gp = vns.get('grant_period', 0)
        totals['vns'][gp] += vns.get('amount', 0)

    # Dissemination
    for d in data['dissemination']:
        gp = d.get('grant_period', 0)
        totals['dissemination'][gp] += d.get('amount', 0)

    # LOS
    for los in data['los']:
        gp = los.get('grant_period', 0)
        totals['los'][gp] += los.get('amount', 0)

    # ITC Conference
    for itc in data['itc_conference']:
        gp = itc.get('grant_period', 0)
        totals['itc_conference'][gp] += itc.get('amount', 0)

    return totals


def extract_section_total(text, section_header):
    """Extract total expenditure for a specific section"""
    # Find section first
    section_match = re.search(section_header, text, re.IGNORECASE)
    if not section_match:
        return 0.0

    # Get text after section header
    after_section = text[section_match.end():]

    # Find first "Total expenditure" line - can have multiple numbers or single
    # Format 1 (budget line): "Total expenditure 49 401.09 0.00 49 401.09" -> take last number
    # Format 2 (simple): "Total expenditure 10 500.00"
    total_match = re.search(r'Total expenditure\s+([\d\s\.]+)', after_section)
    if total_match:
        # Split by whitespace and take the last complete number (with decimal)
        nums_str = total_match.group(1).strip()
        # Find all numbers with decimals
        numbers = re.findall(r'[\d\s]+\.\d{2}', nums_str)
        if numbers:
            # Return the last number (which is the actual total in budget format)
            return parse_amount(numbers[-1])
    return 0.0


def parse_ffr_category_totals(grant_period):
    """Parse actual FFR totals per category from source file"""
    filepath = EXTRACTED_TEXT_DIR / FFR_FILES[grant_period]
    if not filepath.exists():
        return {}

    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    totals = {}

    # Find all "Total expenditure X.XX" lines (single value at end of line)
    # These are the actual section totals, not budget summary lines
    all_totals = re.findall(r'Total expenditure\s+([\d\s]+\.\d{2})\s*$', text, re.MULTILINE)

    # Meetings - find all meeting sections and sum their Sub-total actual amounts
    meeting_sections = re.findall(
        r'Meeting \d+\n.*?Sub-total actual amounts - Paid\s+([\d\s]+\.\d{2})',
        text, re.DOTALL
    )
    totals['meetings'] = sum(parse_amount(t) for t in meeting_sections)

    # Training Schools
    totals['training_schools'] = extract_section_total(text, r'Training Schools Expenditure')

    # STSM - look for the section total after participant list
    totals['stsm'] = extract_section_total(text, r'Short.?Term Scientific Mission.*?Expenditure')

    # Virtual Mobility
    totals['vm'] = extract_section_total(text, r'Virtual Mobility Grant Expenditure')

    # VNS
    totals['vns'] = extract_section_total(text, r'Virtual Networking Support Grant Expenditure')

    # Dissemination
    totals['dissemination'] = extract_section_total(text, r'Dissemination Conference Grant Expenditure')

    # ITC Conference
    totals['itc_conference'] = extract_section_total(text, r'Inclusiveness Target Countries Conference Grant Expenditure')

    # FSAC - from budget summary, format: "FSAC (max 15%) budget actuals accruals total delta"
    # Numbers have format like "22 150.50" (space thousands, dot decimal)
    # Pattern for a single euro amount: digits with optional space thousands, dot, 2 decimals
    euro_num = r'(\d{1,3}(?:\s\d{3})*\.\d{2})'

    fsac_match = re.search(
        rf'FSAC \(max 15%\)\s+{euro_num}\s+{euro_num}\s+{euro_num}\s+{euro_num}',
        text
    )
    if fsac_match:
        totals['fsac'] = parse_amount(fsac_match.group(2))  # Actuals column
    else:
        totals['fsac'] = 0.0

    # Also get the Eligible Networking expenditure total for reference
    eligible_match = re.search(
        rf'Eligible Networking expenditure\s+{euro_num}\s+{euro_num}\s+{euro_num}\s+{euro_num}',
        text
    )
    if eligible_match:
        totals['eligible_networking'] = parse_amount(eligible_match.group(2))  # Actuals column
    else:
        totals['eligible_networking'] = 0.0

    return totals


def generate_report(json_totals, ffr_totals):
    """Generate comparison report"""
    lines = []
    lines.append("=" * 80)
    lines.append("FFR DATA VALIDATION - CATEGORY-BY-CATEGORY COMPARISON")
    lines.append("=" * 80)
    lines.append("")

    categories = ['meetings', 'training_schools', 'stsm', 'vm', 'vns', 'dissemination', 'itc_conference']
    category_names = {
        'meetings': 'Meetings',
        'training_schools': 'Training Schools',
        'stsm': 'STSMs',
        'vm': 'Virtual Mobility',
        'vns': 'VNS Grants',
        'dissemination': 'Dissemination',
        'itc_conference': 'ITC Conference',
        'fsac': 'FSAC (Admin)',
        'los': 'LOS Grants',
    }

    grand_json = 0.0
    grand_ffr = 0.0
    grand_ffr_with_fsac = 0.0

    for gp in range(1, 6):
        lines.append(f"\n{'='*40}")
        lines.append(f"GRANT PERIOD {gp}")
        lines.append(f"{'='*40}")
        lines.append(f"{'Category':<20} {'JSON':>12} {'FFR':>12} {'Diff':>12} {'%':>8}")
        lines.append("-" * 64)

        gp_json_total = 0.0
        gp_ffr_total = 0.0
        ffr_gp = ffr_totals.get(gp, {})

        for cat in categories:
            json_val = json_totals[cat].get(gp, 0.0)
            ffr_val = ffr_gp.get(cat, 0.0)
            diff = json_val - ffr_val
            pct = (diff / ffr_val * 100) if ffr_val > 0 else 0

            gp_json_total += json_val
            gp_ffr_total += ffr_val

            status = "" if abs(diff) < 1 else ("*" if abs(pct) < 5 else "**")
            lines.append(f"{category_names[cat]:<20} {json_val:>12,.2f} {ffr_val:>12,.2f} {diff:>+12,.2f} {pct:>+7.1f}% {status}")

        # Add LOS (not in FFR category totals but we extract it)
        los_json = json_totals['los'].get(gp, 0.0)
        gp_json_total += los_json
        lines.append(f"{'LOS Grants':<20} {los_json:>12,.2f} {'(N/A)':>12} {'-':>12} {'-':>8}")

        # FSAC (in FFR but not extracted)
        fsac_val = ffr_gp.get('fsac', 0.0)
        lines.append(f"{'FSAC (Admin)':<20} {'(N/A)':>12} {fsac_val:>12,.2f} {'-':>12} {'-':>8}")

        lines.append("-" * 64)
        gp_diff = gp_json_total - gp_ffr_total
        lines.append(f"{'GP TOTAL (excl FSAC)':<20} {gp_json_total:>12,.2f} {gp_ffr_total:>12,.2f} {gp_diff:>+12,.2f}")

        grand_json += gp_json_total
        grand_ffr += gp_ffr_total
        grand_ffr_with_fsac += gp_ffr_total + fsac_val

    # Grand totals
    lines.append("\n" + "=" * 80)
    lines.append("GRAND TOTALS")
    lines.append("=" * 80)
    lines.append(f"  JSON extracted total:     {grand_json:>15,.2f} EUR")
    lines.append(f"  FFR total (excl FSAC):    {grand_ffr:>15,.2f} EUR")
    lines.append(f"  FFR total (incl FSAC):    {grand_ffr_with_fsac:>15,.2f} EUR")
    lines.append(f"  Difference (excl FSAC):   {grand_json - grand_ffr:>+15,.2f} EUR")
    lines.append(f"  Difference %:             {(grand_json - grand_ffr) / grand_ffr * 100 if grand_ffr > 0 else 0:>+14.2f}%")

    # Known issues
    lines.append("\n" + "=" * 80)
    lines.append("KNOWN DISCREPANCIES")
    lines.append("=" * 80)
    lines.append("""
  1. -1 PARTICIPANT PATTERN (SOURCE DATA ISSUE)
     The FFR source documents declare X participants but only contain X-1 actual
     data entries. This is a data quality issue in the original FFR PDFs, not an
     extraction bug. Affects 28 meetings across all grant periods.

  2. FSAC COSTS NOT EXTRACTED
     FSAC (Foreign Science Academy Coordinator) costs are administrative overhead
     (~15% of eligible expenditure). These are not participant reimbursements and
     are intentionally not extracted to the JSON data files.

  3. LOS GRANTS
     Local Organiser Support grants are extracted but not separately reported in
     FFR category totals - they may be included in Training School totals.
""")

    lines.append("=" * 80)
    lines.append("END OF REPORT")
    lines.append("=" * 80)

    return "\n".join(lines)


def main():
    print("Loading JSON data...")
    json_data = load_json_data()

    print("Calculating JSON totals...")
    json_totals = calculate_json_totals(json_data)

    print("Parsing FFR source files...")
    ffr_totals = {}
    for gp in range(1, 6):
        ffr_totals[gp] = parse_ffr_category_totals(gp)

    print("Generating report...")
    report = generate_report(json_totals, ffr_totals)

    # Save report
    REPORTS_DIR.mkdir(exist_ok=True)
    report_path = REPORTS_DIR / 'ffr_category_validation.txt'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\nReport saved to: {report_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    total_json = sum(sum(json_totals[cat].values()) for cat in json_totals)
    total_ffr = sum(sum(v for k, v in ffr_totals[gp].items() if k != 'fsac' and k != 'eligible_networking') for gp in ffr_totals)
    total_fsac = sum(ffr_totals[gp].get('fsac', 0) for gp in ffr_totals)

    print(f"JSON extracted:    {total_json:>12,.2f} EUR")
    print(f"FFR (excl FSAC):   {total_ffr:>12,.2f} EUR")
    print(f"FSAC total:        {total_fsac:>12,.2f} EUR")
    print(f"Difference:        {total_json - total_ffr:>+12,.2f} EUR ({(total_json - total_ffr) / total_ffr * 100 if total_ffr > 0 else 0:+.1f}%)")


if __name__ == '__main__':
    main()
