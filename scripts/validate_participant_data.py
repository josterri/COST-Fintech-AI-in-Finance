"""
Comprehensive Participant Data Validation Script
Validates participant_master.json against FFR source files

Detects:
1. Within-meeting duplicate participants
2. Name variants (fuzzy matching)
3. Space-separated thousands parsing bug (amounts differing by exactly 1000)
4. Sum reconciliation at all levels

Author: Claude Code
Date: 2026-01-12
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from difflib import SequenceMatcher

# Paths
PROJECT_DIR = Path(__file__).parent.parent
DATA_DIR = PROJECT_DIR / "data"
REPORTS_DIR = PROJECT_DIR / "reports"
FFR_DIR = Path(r"D:\Joerg\Research\slides\COST_Work_and_Budget_Plans\extracted_text")

# FFR files
FFR_FILES = {
    1: "AGA-CA19130-1-FFR_ID2193.txt",
    2: "AGA-CA19130-2-FFR_ID2346.txt",
    3: "AGA-CA19130-3-FFR_ID2998.txt",
    4: "AGA-CA19130-4-FFR_ID3993.txt",
    5: "AGA-CA19130-5-FFR_ID4828.txt",
}

# Expected totals from FFR (verified)
# Note: These are "Total eligible expenditure" which includes FSAC (~15% admin overhead)
EXPECTED_GP_TOTALS = {
    1: 47459.83,
    2: 33770.46,
    3: 166262.38,
    4: 256854.39,
    5: 270315.26,
}
EXPECTED_GRAND_TOTAL = 774662.32  # Includes FSAC (~100K EUR admin costs)

# FSAC costs by grant period (administrative overhead, not participant data)
FSAC_COSTS = {
    1: 6190.41,
    2: 4404.84,
    3: 21686.40,
    4: 33502.75,
    5: 35258.51,
}
EXPECTED_GRAND_TOTAL_EXCL_FSAC = EXPECTED_GRAND_TOTAL - sum(FSAC_COSTS.values())  # ~673,619.41 EUR


def load_json(filename):
    """Load JSON file with UTF-8 encoding"""
    filepath = DATA_DIR / filename
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_ffr(gp):
    """Load FFR text file"""
    filepath = FFR_DIR / FFR_FILES[gp]
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def normalize_name(name):
    """Normalize name for comparison"""
    name = name.lower().strip()
    # Handle "Lastname, Firstname" format
    if ',' in name:
        parts = name.split(',', 1)
        if len(parts) == 2:
            name = f"{parts[1].strip()} {parts[0].strip()}"
    # Remove special chars, accents
    name = re.sub(r'[,\(\)\-\.\'\"]+', ' ', name)
    # Normalize unicode
    replacements = {
        'ö': 'o', 'ü': 'u', 'ä': 'a', 'ß': 'ss',
        'ø': 'o', 'å': 'a', 'æ': 'ae',
        'č': 'c', 'ć': 'c', 'ş': 's', 'ș': 's',
        'ž': 'z', 'đ': 'd', 'ı': 'i', 'ğ': 'g',
        'ń': 'n', 'ł': 'l', 'ę': 'e', 'ą': 'a',
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'á': 'a', 'à': 'a', 'â': 'a', 'ã': 'a',
        'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
        'ó': 'o', 'ò': 'o', 'ô': 'o', 'õ': 'o',
        'ú': 'u', 'ù': 'u', 'û': 'u',
        'ý': 'y', 'ÿ': 'y',
        'ñ': 'n', 'ç': 'c',
    }
    for old, new in replacements.items():
        name = name.replace(old, new)
    name = ' '.join(name.split())
    return name


def similarity(a, b):
    """Calculate string similarity ratio"""
    return SequenceMatcher(None, a, b).ratio()


def parse_eur_amount(text):
    """Parse European format EUR amount (space as thousands separator)"""
    if not text:
        return 0.0
    # Remove EUR symbol and extra spaces
    text = text.replace('EUR', '').strip()
    # Handle space-separated thousands: "1 011.15" -> "1011.15"
    text = re.sub(r'(\d)\s+(\d)', r'\1\2', text)
    # Replace comma decimal separator if present
    if ',' in text and '.' not in text:
        text = text.replace(',', '.')
    elif ',' in text and '.' in text:
        # Format like "1.234,56" -> "1234.56"
        text = text.replace('.', '').replace(',', '.')
    try:
        return float(text)
    except ValueError:
        return 0.0


def extract_ffr_meeting_participants(ffr_text, gp):
    """Extract meeting participants from FFR text"""
    meetings = {}

    # Split by Meeting headers
    meeting_sections = re.split(r'\nMeeting (\d+)\n', ffr_text)

    for i in range(1, len(meeting_sections), 2):
        if i + 1 >= len(meeting_sections):
            break

        meeting_num = int(meeting_sections[i])
        section = meeting_sections[i + 1]

        # Stop at Training Schools or next major section
        stop_markers = [
            'Training Schools Expenditure',
            'Training School 1',
            'Short-Term Scientific Missions',
            'Virtual Mobility',
            'Virtual Networking Support',
            'Dissemination'
        ]
        for marker in stop_markers:
            if marker in section:
                section = section.split(marker)[0]

        meeting_id = f"GP{gp}_M{meeting_num}"
        participants = []

        # Extract title
        title_match = re.search(r'Meeting title\s+(.+?)(?=\n|Meeting type)', section, re.DOTALL)
        title = title_match.group(1).strip() if title_match else ""

        # Extract participant count from FFR
        count_match = re.search(r'Total number of reimbursed participants\s+(\d+)', section)
        expected_count = int(count_match.group(1)) if count_match else 0

        # Pattern for participant lines
        # Format: "1 Name, First Country 123.45 678.90 0.00 802.35"
        euro_pattern = r'(\d{1,3}(?:\s\d{3})*[,\.]\d{2})'
        participant_pattern = rf'^\s*(\d+)\s+([A-Za-z\u00C0-\u024F\s,\(\)\-\.\'\"]+?)\s+([A-Z]{{2}})\s+{euro_pattern}\s+{euro_pattern}\s+{euro_pattern}\s+{euro_pattern}\s*$'

        for line in section.split('\n'):
            match = re.match(participant_pattern, line.strip())
            if match:
                idx, name, country, travel, daily, other, total = match.groups()
                participants.append({
                    'index': int(idx),
                    'name': name.strip(),
                    'country': country,
                    'travel': parse_eur_amount(travel),
                    'daily': parse_eur_amount(daily),
                    'other': parse_eur_amount(other),
                    'total': parse_eur_amount(total),
                })

        meetings[meeting_id] = {
            'title': title,
            'expected_count': expected_count,
            'participants': participants,
        }

    return meetings


def detect_within_meeting_duplicates(meetings_data):
    """Detect same participant appearing multiple times in same meeting"""
    duplicates = []

    for meeting in meetings_data:
        meeting_id = meeting['id']
        title = meeting.get('title', '')
        participants = meeting.get('participants', [])

        # Group by normalized name
        name_groups = defaultdict(list)
        for p in participants:
            key = normalize_name(p['name'])
            name_groups[key].append(p)

        # Find duplicates
        for norm_name, entries in name_groups.items():
            if len(entries) > 1:
                duplicates.append({
                    'meeting_id': meeting_id,
                    'title': title,
                    'name': entries[0]['name'],
                    'normalized': norm_name,
                    'count': len(entries),
                    'amounts': [e['total'] for e in entries],
                    'total_in_json': sum(e['total'] for e in entries),
                })

    return duplicates


def detect_participant_count_mismatch(json_meetings, ffr_meetings):
    """Detect meetings where participant count doesn't match FFR"""
    mismatches = []

    for meeting in json_meetings:
        meeting_id = meeting['id']
        json_count = len(meeting.get('participants', []))

        if meeting_id in ffr_meetings:
            ffr_info = ffr_meetings[meeting_id]
            ffr_count = ffr_info['expected_count']
            ffr_actual = len(ffr_info['participants'])

            if json_count != ffr_count:
                mismatches.append({
                    'meeting_id': meeting_id,
                    'title': meeting.get('title', ''),
                    'json_count': json_count,
                    'ffr_expected': ffr_count,
                    'ffr_parsed': ffr_actual,
                    'difference': json_count - ffr_count,
                })

    return mismatches


def detect_thousands_parsing_bug(json_meetings, ffr_meetings):
    """Detect amounts that differ by exactly 1000 EUR (thousands parsing bug)"""
    discrepancies = []

    for meeting in json_meetings:
        meeting_id = meeting['id']

        if meeting_id not in ffr_meetings:
            continue

        ffr_info = ffr_meetings[meeting_id]
        ffr_by_name = {normalize_name(p['name']): p for p in ffr_info['participants']}

        for p in meeting.get('participants', []):
            norm_name = normalize_name(p['name'])
            json_amount = p['total']

            if norm_name in ffr_by_name:
                ffr_amount = ffr_by_name[norm_name]['total']
                diff = ffr_amount - json_amount

                # Check for thousands parsing bug (diff is ~1000, ~2000, etc.)
                if abs(diff) >= 999 and abs(diff % 1000) < 2:
                    discrepancies.append({
                        'meeting_id': meeting_id,
                        'name': p['name'],
                        'json_amount': json_amount,
                        'ffr_amount': ffr_amount,
                        'difference': diff,
                        'likely_thousands_bug': True,
                    })
                elif abs(diff) > 1:
                    discrepancies.append({
                        'meeting_id': meeting_id,
                        'name': p['name'],
                        'json_amount': json_amount,
                        'ffr_amount': ffr_amount,
                        'difference': diff,
                        'likely_thousands_bug': False,
                    })

    return discrepancies


def detect_name_variants(participant_master):
    """Detect potential name variants that might be same person"""
    variants = []
    names = [(p['name'], normalize_name(p['name'])) for p in participant_master]

    # Compare all pairs
    for i, (name1, norm1) in enumerate(names):
        for j, (name2, norm2) in enumerate(names):
            if i >= j:
                continue

            # Check if normalized names are similar but not identical
            sim = similarity(norm1, norm2)
            if 0.85 <= sim < 1.0:
                # Get the participant records
                p1 = participant_master[i]
                p2 = participant_master[j]

                variants.append({
                    'name1': name1,
                    'name2': name2,
                    'similarity': sim,
                    'total1': p1['total_reimbursed'],
                    'total2': p2['total_reimbursed'],
                    'countries1': p1.get('countries', []),
                    'countries2': p2.get('countries', []),
                })

    return variants


def reconcile_meeting_sums(json_meetings, ffr_meetings):
    """Reconcile meeting-level sums"""
    results = []

    for meeting in json_meetings:
        meeting_id = meeting['id']
        json_sum = sum(p['total'] for p in meeting.get('participants', []))

        ffr_sum = None
        if meeting_id in ffr_meetings:
            ffr_sum = sum(p['total'] for p in ffr_meetings[meeting_id]['participants'])

        diff = (json_sum - ffr_sum) if ffr_sum is not None else None

        results.append({
            'meeting_id': meeting_id,
            'json_sum': json_sum,
            'ffr_sum': ffr_sum,
            'difference': diff,
            'status': 'OK' if diff is not None and abs(diff) < 1 else 'MISMATCH' if diff else 'NO_FFR_DATA',
        })

    return results


def reconcile_participant_totals(participant_master):
    """Verify participant total_reimbursed matches sum of activities"""
    discrepancies = []

    for p in participant_master:
        calculated = 0.0

        # Sum all activities
        for m in p.get('meetings', []):
            calculated += m.get('amount', 0)
        for s in p.get('stsm', []):
            calculated += s.get('amount', 0)
        for v in p.get('virtual_mobility', []):
            calculated += v.get('amount', 0)
        for t in p.get('training_schools', []):
            calculated += t.get('amount', 0)
        for i in p.get('itc_conferences', []):
            calculated += i.get('amount', 0)

        stored = p.get('total_reimbursed', 0)
        diff = abs(stored - calculated)

        if diff > 0.01:
            discrepancies.append({
                'name': p['name'],
                'stored_total': stored,
                'calculated_total': calculated,
                'difference': stored - calculated,
            })

    return discrepancies


def generate_report(findings):
    """Generate comprehensive validation report"""
    lines = []
    lines.append("=" * 80)
    lines.append("PARTICIPANT DATA VALIDATION REPORT")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 80)
    lines.append("")

    # Summary
    lines.append("SUMMARY")
    lines.append("-" * 40)
    lines.append(f"  Within-meeting duplicates: {len(findings['duplicates'])}")
    lines.append(f"  Participant count mismatches: {len(findings['count_mismatches'])}")
    lines.append(f"  Thousands parsing bugs: {len([d for d in findings['amount_discrepancies'] if d['likely_thousands_bug']])}")
    lines.append(f"  Other amount discrepancies: {len([d for d in findings['amount_discrepancies'] if not d['likely_thousands_bug']])}")
    lines.append(f"  Potential name variants: {len(findings['name_variants'])}")
    lines.append(f"  Total reconciliation errors: {len([r for r in findings['meeting_sums'] if r['status'] == 'MISMATCH'])}")
    lines.append("")

    # Within-meeting duplicates
    lines.append("=" * 80)
    lines.append("WITHIN-MEETING DUPLICATES")
    lines.append("=" * 80)

    if findings['duplicates']:
        # Group by meeting
        by_meeting = defaultdict(list)
        for d in findings['duplicates']:
            by_meeting[d['meeting_id']].append(d)

        for meeting_id, dups in sorted(by_meeting.items()):
            lines.append(f"\n{meeting_id}: {dups[0]['title'][:60]}...")
            for d in dups:
                amounts_str = ', '.join(f"{a:.2f}" for a in d['amounts'])
                lines.append(f"  - {d['name']} appears {d['count']}x: [{amounts_str}]")
                lines.append(f"    Total in JSON: {d['total_in_json']:.2f} EUR")
    else:
        lines.append("  No duplicates found.")
    lines.append("")

    # Participant count mismatches
    lines.append("=" * 80)
    lines.append("PARTICIPANT COUNT MISMATCHES (JSON vs FFR)")
    lines.append("=" * 80)

    if findings['count_mismatches']:
        for m in sorted(findings['count_mismatches'], key=lambda x: -abs(x['difference'])):
            lines.append(f"\n{m['meeting_id']}: {m['title'][:50]}...")
            lines.append(f"  JSON count: {m['json_count']}")
            lines.append(f"  FFR expected: {m['ffr_expected']}")
            lines.append(f"  DIFFERENCE: {m['difference']:+d}")
    else:
        lines.append("  All counts match.")
    lines.append("")

    # Thousands parsing bug
    lines.append("=" * 80)
    lines.append("THOUSANDS PARSING BUG (Amounts differing by ~1000 EUR)")
    lines.append("=" * 80)

    thousands_bugs = [d for d in findings['amount_discrepancies'] if d['likely_thousands_bug']]
    if thousands_bugs:
        lines.append(f"\nTotal entries affected: {len(thousands_bugs)}")
        total_missing = sum(d['difference'] for d in thousands_bugs)
        lines.append(f"Total amount missing: {total_missing:,.2f} EUR")
        lines.append("")

        for d in sorted(thousands_bugs, key=lambda x: -x['difference'])[:30]:
            lines.append(f"  {d['name']} - {d['meeting_id']}")
            lines.append(f"    FFR: {d['ffr_amount']:,.2f} | JSON: {d['json_amount']:,.2f} | Diff: {d['difference']:+,.2f}")

        if len(thousands_bugs) > 30:
            lines.append(f"\n  ... and {len(thousands_bugs) - 30} more entries")
    else:
        lines.append("  No thousands parsing bugs detected.")
    lines.append("")

    # Other discrepancies
    lines.append("=" * 80)
    lines.append("OTHER AMOUNT DISCREPANCIES")
    lines.append("=" * 80)

    other_discrepancies = [d for d in findings['amount_discrepancies'] if not d['likely_thousands_bug']]
    if other_discrepancies:
        for d in sorted(other_discrepancies, key=lambda x: -abs(x['difference']))[:20]:
            lines.append(f"  {d['name']} - {d['meeting_id']}")
            lines.append(f"    FFR: {d['ffr_amount']:,.2f} | JSON: {d['json_amount']:,.2f} | Diff: {d['difference']:+,.2f}")
    else:
        lines.append("  No other discrepancies found.")
    lines.append("")

    # Name variants
    lines.append("=" * 80)
    lines.append("POTENTIAL NAME VARIANTS (may be same person)")
    lines.append("=" * 80)

    if findings['name_variants']:
        for v in sorted(findings['name_variants'], key=lambda x: -x['similarity'])[:20]:
            lines.append(f"\n  '{v['name1']}' vs '{v['name2']}'")
            lines.append(f"    Similarity: {v['similarity']:.2%}")
            lines.append(f"    Totals: {v['total1']:,.2f} vs {v['total2']:,.2f} EUR")
            lines.append(f"    Countries: {v['countries1']} vs {v['countries2']}")
    else:
        lines.append("  No potential name variants found.")
    lines.append("")

    # Meeting sum reconciliation
    lines.append("=" * 80)
    lines.append("MEETING SUM RECONCILIATION")
    lines.append("=" * 80)

    mismatched = [r for r in findings['meeting_sums'] if r['status'] == 'MISMATCH']
    if mismatched:
        lines.append(f"\nMeetings with sum mismatches: {len(mismatched)}")
        total_diff = sum(r['difference'] for r in mismatched if r['difference'])
        lines.append(f"Total discrepancy: {total_diff:,.2f} EUR")
        lines.append("")

        for r in sorted(mismatched, key=lambda x: -abs(x['difference'] or 0))[:20]:
            lines.append(f"  {r['meeting_id']}")
            lines.append(f"    JSON sum: {r['json_sum']:,.2f} | FFR sum: {r['ffr_sum']:,.2f}")
            lines.append(f"    Difference: {r['difference']:+,.2f} EUR")
    else:
        lines.append("  All meeting sums reconcile correctly.")
    lines.append("")

    # Participant total reconciliation
    lines.append("=" * 80)
    lines.append("PARTICIPANT TOTAL RECONCILIATION")
    lines.append("=" * 80)

    if findings['participant_totals']:
        lines.append(f"\nParticipants with internal sum errors: {len(findings['participant_totals'])}")
        for p in findings['participant_totals'][:20]:
            lines.append(f"  {p['name']}")
            lines.append(f"    Stored: {p['stored_total']:,.2f} | Calculated: {p['calculated_total']:,.2f}")
            lines.append(f"    Difference: {p['difference']:+,.2f} EUR")
    else:
        lines.append("  All participant totals reconcile correctly.")
    lines.append("")

    # Grand totals
    lines.append("=" * 80)
    lines.append("GRAND TOTAL VALIDATION")
    lines.append("=" * 80)

    json_grand = findings['json_grand_total']
    ffr_grand = EXPECTED_GRAND_TOTAL
    diff = json_grand - ffr_grand

    lines.append(f"\n  JSON grand total:     {json_grand:>15,.2f} EUR")
    lines.append(f"  FFR expected total:   {ffr_grand:>15,.2f} EUR")
    lines.append(f"  Difference:           {diff:>+15,.2f} EUR")
    lines.append(f"  Status: {'OK' if abs(diff) < 1 else 'MISMATCH'}")
    lines.append("")

    lines.append("=" * 80)
    lines.append("END OF REPORT")
    lines.append("=" * 80)

    return '\n'.join(lines)


def main():
    print("Loading data...")

    # Load JSON data
    meetings_data = load_json('meetings_participants.json')
    participant_master = load_json('participant_master.json')

    # Load all additional categories for correct grand total
    stsms = load_json('stsm_full.json')
    vms = load_json('virtual_mobility_full.json')
    training_schools = load_json('training_school_attendees.json')
    vns = load_json('vns_grants.json')
    dissemination = load_json('dissemination_grants.json')
    los = load_json('los_grants.json')

    # Load and parse all FFR files
    print("Parsing FFR source files...")
    all_ffr_meetings = {}
    for gp in range(1, 6):
        ffr_text = load_ffr(gp)
        gp_meetings = extract_ffr_meeting_participants(ffr_text, gp)
        all_ffr_meetings.update(gp_meetings)

    print(f"Parsed {len(all_ffr_meetings)} meetings from FFR files")

    # Calculate correct grand total from ALL categories
    meeting_total = sum(sum(p['total'] for p in m['participants']) for m in meetings_data if m.get('participants'))
    stsm_total = sum(s['amount'] for s in stsms)
    vm_total = sum(v['amount'] for v in vms)
    ts_total = sum(sum(p.get('total', 0) for p in ts.get('participants', [])) for ts in training_schools)
    vns_total = sum(v['amount'] for v in vns)
    diss_total = sum(d.get('amount', 0) for d in dissemination)
    los_total = sum(l.get('amount', 0) for l in los)

    json_grand_total = meeting_total + stsm_total + vm_total + ts_total + vns_total + diss_total + los_total

    # Run all validations
    print("Running validations...")

    findings = {
        'duplicates': detect_within_meeting_duplicates(meetings_data),
        'count_mismatches': detect_participant_count_mismatch(meetings_data, all_ffr_meetings),
        'amount_discrepancies': detect_thousands_parsing_bug(meetings_data, all_ffr_meetings),
        'name_variants': detect_name_variants(participant_master),
        'meeting_sums': reconcile_meeting_sums(meetings_data, all_ffr_meetings),
        'participant_totals': reconcile_participant_totals(participant_master),
        'json_grand_total': json_grand_total,
        'category_totals': {
            'meetings': meeting_total,
            'stsm': stsm_total,
            'vm': vm_total,
            'training_schools': ts_total,
            'vns': vns_total,
            'dissemination': diss_total,
            'los': los_total,
        },
    }

    # Generate report
    print("Generating report...")
    report = generate_report(findings)

    # Save report
    REPORTS_DIR.mkdir(exist_ok=True)
    report_path = REPORTS_DIR / 'participant_data_validation.txt'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    # Also save JSON findings
    json_findings = {
        'duplicates': findings['duplicates'],
        'count_mismatches': findings['count_mismatches'],
        'amount_discrepancies': findings['amount_discrepancies'],
        'name_variants': findings['name_variants'],
        'category_totals': findings['category_totals'],
        'json_grand_total': findings['json_grand_total'],
        'expected_grand_total': EXPECTED_GRAND_TOTAL,
        'expected_grand_total_excl_fsac': EXPECTED_GRAND_TOTAL_EXCL_FSAC,
    }
    json_path = REPORTS_DIR / 'participant_data_validation.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_findings, f, indent=2, ensure_ascii=False)

    print(f"\nReport saved to: {report_path}")
    print(f"JSON findings saved to: {json_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Within-meeting duplicates: {len(findings['duplicates'])}")
    print(f"Participant count mismatches: {len(findings['count_mismatches'])}")
    print(f"  (Note: -1 pattern is FFR source data issue, not extraction bug)")
    print(f"Thousands parsing bugs: {len([d for d in findings['amount_discrepancies'] if d['likely_thousands_bug']])}")
    print()
    print("Category totals extracted:")
    for cat, val in findings['category_totals'].items():
        print(f"  {cat:<20} {val:>12,.2f} EUR")
    print()
    print(f"JSON grand total:         {findings['json_grand_total']:>12,.2f} EUR")
    print(f"FFR total (incl FSAC):    {EXPECTED_GRAND_TOTAL:>12,.2f} EUR")
    print(f"FFR total (excl FSAC):    {EXPECTED_GRAND_TOTAL_EXCL_FSAC:>12,.2f} EUR")
    print(f"Difference (excl FSAC):   {findings['json_grand_total'] - EXPECTED_GRAND_TOTAL_EXCL_FSAC:>+12,.2f} EUR")


if __name__ == '__main__':
    main()
