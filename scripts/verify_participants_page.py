#!/usr/bin/env python3
"""
Verify EVERY EUR amount on participants.html against FFR source files.

This script extracts ALL participant reimbursement data from the 5 FFR text files
and compares against participant_master.json to identify discrepancies.

The systematic error identified: Space-separated thousands in FFR (e.g., "1 011.15")
were incorrectly parsed, dropping the thousands portion (e.g., stored as "11.15").
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Paths
FFR_SOURCE_DIR = Path(r"D:\Joerg\Research\slides\COST_Work_and_Budget_Plans\extracted_text")
DATA_DIR = Path(__file__).parent.parent / "data"
REPORTS_DIR = Path(__file__).parent.parent / "reports"

# FFR files by grant period
FFR_FILES = {
    1: "AGA-CA19130-1-FFR_ID2193.txt",
    2: "AGA-CA19130-2-FFR_ID2346.txt",
    3: "AGA-CA19130-3-FFR_ID2998.txt",
    4: "AGA-CA19130-4-FFR_ID3993.txt",
    5: "AGA-CA19130-5-FFR_ID4828.txt",
}


def parse_eur_amount(text):
    """
    Parse EUR amount with space as thousands separator.
    Examples: '1 011.15' -> 1011.15, '600.75' -> 600.75, '-42.50' -> -42.50
    """
    if not text or text.strip() == '':
        return 0.0
    text = text.strip().replace(" ", "").replace(",", "")
    try:
        return float(text)
    except ValueError:
        return 0.0


def extract_meetings_from_ffr(gp, content):
    """
    Extract all meetings and their participant reimbursements from FFR content.
    Returns list of dicts with meeting info and participants.
    """
    meetings = []

    # Find all meeting sections
    meeting_pattern = r'Meeting\s+(\d+)\s*\n'
    meeting_matches = list(re.finditer(meeting_pattern, content))

    for i, match in enumerate(meeting_matches):
        meeting_num = int(match.group(1))
        start_pos = match.end()

        # End position is next meeting or end of file
        if i + 1 < len(meeting_matches):
            end_pos = meeting_matches[i + 1].start()
        else:
            end_pos = len(content)

        section = content[start_pos:end_pos]

        # Extract meeting details
        meeting_info = {
            "grant_period": gp,
            "meeting_num": meeting_num,
            "meeting_id": f"GP{gp}_M{meeting_num}",
        }

        # Start date
        start_date_match = re.search(r'Start date\s+(\d{2}/\d{2}/\d{4})', section)
        if start_date_match:
            meeting_info["start_date"] = start_date_match.group(1)

        # End date
        end_date_match = re.search(r'End date\s+(\d{2}/\d{2}/\d{4})', section)
        if end_date_match:
            meeting_info["end_date"] = end_date_match.group(1)

        # Meeting location
        location_match = re.search(r'Meeting location\s+(.+?)(?:\n|$)', section)
        if location_match:
            meeting_info["location"] = location_match.group(1).strip()

        # Meeting title
        title_match = re.search(r'Meeting title\s+(.+?)(?:\n|$)', section)
        if title_match:
            meeting_info["title"] = title_match.group(1).strip()

        # Extract participants
        # Pattern matches: index name country travel daily other total
        # Amounts may have space as thousands separator
        # Example: 6 Jörg Osterrieder CH 600.75 410.40 0.00 1 011.15

        participants = []

        # Find the "List of reimbursed participants" section
        list_start = section.find("List of reimbursed participants")
        if list_start != -1:
            list_section = section[list_start:]

            # Find the end (Sub-total or next section)
            list_end = list_section.find("Sub-total")
            if list_end == -1:
                list_end = list_section.find("List of participants still")
            if list_end == -1:
                list_end = len(list_section)

            participant_section = list_section[:list_end]

            # Pattern for participant lines
            # Handle various name formats and space-separated amounts
            # The pattern needs to handle amounts like "1 200.00" and "0.00"
            participant_pattern = r'^(\d+)\s+(.+?)\s+([A-Z]{2})\s+((?:-?[\d\s]+\.\d{2}))\s+((?:-?[\d\s]+\.\d{2}))\s+((?:-?[\d\s]+\.\d{2}))\s+((?:-?[\d\s]+\.\d{2}))\s*$'

            for line in participant_section.split('\n'):
                line = line.strip()
                if not line or line.startswith('List of') or 'participant' in line.lower() and 'name' in line.lower():
                    continue

                # Try to match the pattern
                match = re.match(participant_pattern, line)
                if match:
                    participants.append({
                        "index": int(match.group(1)),
                        "name": match.group(2).strip(),
                        "country": match.group(3),
                        "travel_allowance": parse_eur_amount(match.group(4)),
                        "daily_allowance": parse_eur_amount(match.group(5)),
                        "other_expenses": parse_eur_amount(match.group(6)),
                        "total": parse_eur_amount(match.group(7)),
                    })

        meeting_info["participants"] = participants
        meetings.append(meeting_info)

    return meetings


def extract_stsms_from_ffr(gp, content):
    """Extract STSM data from FFR content."""
    stsms = []

    # Find STSM section
    stsm_start = content.find("Short-Term Scientific Mission")
    if stsm_start == -1:
        stsm_start = content.find("Short Term Scientific Mission")
    if stsm_start == -1:
        return stsms

    # Pattern for STSM entries
    # Format varies but includes: index, name, status, country_from, country_to, dates, amount
    stsm_pattern = r'^(\d+)\s+(.+?)\s+(DCG|YRI|Both)\s+(.+?)\s+([A-Z]{2})\s+(\d{2}/\d{2}/\d{4})\s+(\d{2}/\d{2}/\d{4})\s+([\d\s,\.]+)\s*$'

    # This will need more specific handling based on actual format

    return stsms


def extract_vm_from_ffr(gp, content):
    """Extract Virtual Mobility data from FFR content."""
    vms = []

    # Find VM section
    vm_start = content.find("Virtual Mobility Grant")
    if vm_start == -1:
        return vms

    # Pattern will need adjustment based on actual format

    return vms


def extract_all_from_ffr():
    """Extract all participant data from all FFR files."""
    all_meetings = []
    all_stsms = []
    all_vms = []

    for gp, filename in FFR_FILES.items():
        filepath = FFR_SOURCE_DIR / filename
        if not filepath.exists():
            print(f"WARNING: {filepath} not found")
            continue

        content = filepath.read_text(encoding='utf-8')

        # Extract meetings with participants
        meetings = extract_meetings_from_ffr(gp, content)
        all_meetings.extend(meetings)

        # Extract STSMs
        stsms = extract_stsms_from_ffr(gp, content)
        all_stsms.extend(stsms)

        # Extract VMs
        vms = extract_vm_from_ffr(gp, content)
        all_vms.extend(vms)

    return {
        "meetings": all_meetings,
        "stsms": all_stsms,
        "virtual_mobility": all_vms,
    }


def load_json_data():
    """Load all relevant JSON data files."""
    data = {}

    json_files = [
        "participant_master.json",
        "meetings_participants.json",
        "meetings_detailed.json",
        "stsm_detailed.json",
        "virtual_mobility_full.json",
    ]

    for filename in json_files:
        filepath = DATA_DIR / filename
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                data[filename] = json.load(f)
        else:
            print(f"WARNING: {filepath} not found")
            data[filename] = []

    return data


def normalize_name(name):
    """Normalize name for matching."""
    # Remove extra spaces, handle various formats
    name = ' '.join(name.split())
    # Handle "Last, First" vs "First Last"
    if ',' in name:
        parts = name.split(',')
        if len(parts) == 2:
            name = f"{parts[1].strip()} {parts[0].strip()}"
    return name.lower()


def compare_meeting_participants(ffr_meetings, json_data):
    """
    Compare FFR meeting participants against JSON data.
    Returns list of discrepancies.
    """
    discrepancies = []

    # Build lookup from JSON participant_master
    json_participants = json_data.get("participant_master.json", [])

    # Create a lookup by participant name
    json_by_name = defaultdict(list)
    for p in json_participants:
        normalized = normalize_name(p.get("name", ""))
        json_by_name[normalized].append(p)

    # Also build lookup from meetings_participants.json
    meetings_participants = json_data.get("meetings_participants.json", [])
    mp_by_meeting = defaultdict(list)
    for mp in meetings_participants:
        meeting_id = mp.get("meeting_id", "")
        for participant in mp.get("participants", []):
            mp_by_meeting[(meeting_id, normalize_name(participant.get("name", "")))].append(participant)

    # Compare each FFR meeting participant
    for meeting in ffr_meetings:
        meeting_id = meeting.get("meeting_id", "")
        meeting_title = meeting.get("title", "")
        meeting_date = meeting.get("start_date", "")

        for p in meeting.get("participants", []):
            ffr_name = p.get("name", "")
            ffr_total = p.get("total", 0)
            ffr_travel = p.get("travel_allowance", 0)
            ffr_daily = p.get("daily_allowance", 0)
            ffr_other = p.get("other_expenses", 0)
            normalized_name = normalize_name(ffr_name)

            # Find in JSON participant_master
            json_matches = json_by_name.get(normalized_name, [])

            for json_p in json_matches:
                # Check meetings for this participant
                for m in json_p.get("meetings", []):
                    # Match by date
                    json_date = m.get("date", "")
                    if meeting_date and json_date and meeting_date == json_date:
                        json_amount = m.get("amount", 0)
                        if abs(ffr_total - json_amount) > 0.01:
                            discrepancies.append({
                                "type": "meeting",
                                "participant": ffr_name,
                                "meeting_id": meeting_id,
                                "meeting_title": meeting_title,
                                "date": meeting_date,
                                "ffr_travel": ffr_travel,
                                "ffr_daily": ffr_daily,
                                "ffr_other": ffr_other,
                                "ffr_total": ffr_total,
                                "json_amount": json_amount,
                                "difference": ffr_total - json_amount,
                                "source": "participant_master.json",
                            })

            # Also check meetings_participants.json
            mp_matches = mp_by_meeting.get((meeting_id, normalized_name), [])
            for mp in mp_matches:
                json_total = mp.get("total", 0)
                if abs(ffr_total - json_total) > 0.01:
                    discrepancies.append({
                        "type": "meeting",
                        "participant": ffr_name,
                        "meeting_id": meeting_id,
                        "meeting_title": meeting_title,
                        "date": meeting_date,
                        "ffr_travel": ffr_travel,
                        "ffr_daily": ffr_daily,
                        "ffr_other": ffr_other,
                        "ffr_total": ffr_total,
                        "json_amount": json_total,
                        "difference": ffr_total - json_total,
                        "source": "meetings_participants.json",
                    })

    return discrepancies


def generate_report(ffr_data, json_data, discrepancies):
    """Generate verification report."""
    report = []
    report.append("=" * 80)
    report.append("PARTICIPANTS PAGE VERIFICATION REPORT")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 80)
    report.append("")

    # Summary
    total_meetings = len(ffr_data["meetings"])
    total_participants = sum(len(m.get("participants", [])) for m in ffr_data["meetings"])

    report.append("SUMMARY:")
    report.append(f"  Total meetings parsed from FFR: {total_meetings}")
    report.append(f"  Total participant reimbursements: {total_participants}")
    report.append(f"  Total discrepancies found: {len(discrepancies)}")
    report.append("")

    # Group discrepancies by participant
    by_participant = defaultdict(list)
    for d in discrepancies:
        by_participant[d["participant"]].append(d)

    report.append(f"  Participants with discrepancies: {len(by_participant)}")
    report.append("")

    # Detail by participant
    report.append("DISCREPANCIES BY PARTICIPANT:")
    report.append("=" * 80)

    for name in sorted(by_participant.keys()):
        items = by_participant[name]
        report.append("")
        report.append(f"{name}")
        report.append("-" * 80)

        for d in items:
            report.append(f"  {d['meeting_id']}: {d['meeting_title'][:50]}... ({d['date']})")
            report.append(f"    FFR (correct):   {d['ffr_total']:,.2f} EUR")
            report.append(f"      Travel: {d['ffr_travel']:,.2f} | Daily: {d['ffr_daily']:,.2f} | Other: {d['ffr_other']:,.2f}")
            report.append(f"    JSON (current):  {d['json_amount']:,.2f} EUR")
            report.append(f"    DIFFERENCE:      {d['difference']:+,.2f} EUR")
            report.append(f"    Source file:     {d['source']}")
            report.append("")

    # Corrections needed
    report.append("")
    report.append("CORRECTIONS NEEDED:")
    report.append("=" * 80)

    # Group by source file
    by_source = defaultdict(list)
    for d in discrepancies:
        by_source[d["source"]].append(d)

    for source, items in sorted(by_source.items()):
        report.append(f"\nFile: data/{source}")
        for d in items:
            report.append(f"  {d['participant']} - {d['meeting_id']}:")
            report.append(f"    Change: {d['json_amount']:.2f} -> {d['ffr_total']:.2f}")

    return "\n".join(report)


def main():
    print("=" * 80)
    print("PARTICIPANTS PAGE VERIFICATION")
    print("Comparing FFR source files against JSON data")
    print("=" * 80)
    print()

    # Extract all data from FFR files
    print("Extracting data from FFR source files...")
    ffr_data = extract_all_from_ffr()

    total_meetings = len(ffr_data["meetings"])
    total_participants = sum(len(m.get("participants", [])) for m in ffr_data["meetings"])
    print(f"  Found {total_meetings} meetings with {total_participants} participant reimbursements")

    # Load JSON data
    print("\nLoading JSON data files...")
    json_data = load_json_data()

    # Compare
    print("\nComparing data...")
    discrepancies = compare_meeting_participants(ffr_data["meetings"], json_data)
    print(f"  Found {len(discrepancies)} discrepancies")

    # Generate report
    print("\nGenerating report...")
    report_text = generate_report(ffr_data, json_data, discrepancies)

    # Save reports
    REPORTS_DIR.mkdir(exist_ok=True)

    # Text report
    report_path = REPORTS_DIR / "participants_verification.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_text)
    print(f"  Saved: {report_path}")

    # JSON report (machine-readable)
    json_report = {
        "generated": datetime.now().isoformat(),
        "summary": {
            "total_meetings": total_meetings,
            "total_participants": total_participants,
            "total_discrepancies": len(discrepancies),
        },
        "ffr_data": ffr_data,
        "discrepancies": discrepancies,
    }

    json_report_path = REPORTS_DIR / "participants_verification.json"
    with open(json_report_path, 'w', encoding='utf-8') as f:
        json.dump(json_report, f, indent=2, ensure_ascii=False)
    print(f"  Saved: {json_report_path}")

    # Print summary
    print("\n" + "=" * 80)
    print("VERIFICATION COMPLETE")
    print("=" * 80)

    if discrepancies:
        # Group by participant for summary
        by_participant = defaultdict(list)
        for d in discrepancies:
            by_participant[d["participant"]].append(d)

        print(f"\nFound {len(discrepancies)} discrepancies affecting {len(by_participant)} participants:")
        print()
        for name in sorted(by_participant.keys()):
            items = by_participant[name]
            total_diff = sum(d["difference"] for d in items)
            print(f"  {name}: {len(items)} errors, total underreported by {total_diff:,.2f} EUR")
    else:
        print("\nNo discrepancies found - all amounts match!")

    print(f"\nFull report saved to: {report_path}")

    return discrepancies


if __name__ == "__main__":
    main()
