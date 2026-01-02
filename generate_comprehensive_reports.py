"""
Generate comprehensive HTML reports from Mid-Term Report source documents.
Extracts ALL details: meetings, training schools, STSMs, VMGs, publications, etc.
"""

import re
from pathlib import Path
from datetime import datetime


def read_file(filepath):
    """Read file content."""
    return Path(filepath).read_text(encoding='utf-8')


def extract_sections(text):
    """Extract major sections from the document."""
    sections = {}
    current_section = "header"
    current_content = []

    for line in text.split('\n'):
        # Detect section headers (usually preceded by page markers)
        if line.strip() and len(line.strip()) > 5:
            current_content.append(line)

    return '\n'.join(current_content)


def extract_meetings_and_events(text):
    """Extract all meetings and events from the text."""
    events = []

    # Look for event patterns
    # Pattern for dates with locations
    date_patterns = [
        r'(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
        r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
        r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}[-,]?\s*\d{0,2},?\s*\d{4}',
    ]

    # Extract lines mentioning events
    event_keywords = ['conference', 'workshop', 'meeting', 'seminar', 'school',
                      'symposium', 'event', 'webinar', 'datathon', 'hackathon']

    lines = text.split('\n')
    for i, line in enumerate(lines):
        line_lower = line.lower()
        if any(kw in line_lower for kw in event_keywords):
            # Get context (surrounding lines)
            start = max(0, i-2)
            end = min(len(lines), i+3)
            context = '\n'.join(lines[start:end])
            events.append({
                'line': line.strip(),
                'context': context
            })

    return events


def extract_publications(text):
    """Extract all publications from the text."""
    publications = []

    # Look for DOI patterns
    doi_pattern = r'doi[:\s]*([^\s]+)'

    # Look for publication entries (usually have authors, title, journal)
    lines = text.split('\n')
    current_pub = []

    for line in lines:
        line = line.strip()
        if not line:
            if current_pub:
                pub_text = ' '.join(current_pub)
                if 'doi' in pub_text.lower() or any(year in pub_text for year in ['2020', '2021', '2022', '2023']):
                    publications.append(pub_text)
                current_pub = []
        else:
            current_pub.append(line)

    return publications


def extract_stsms(text):
    """Extract STSM (Short Term Scientific Mission) information."""
    stsms = []

    # Find STSM sections
    lines = text.split('\n')
    in_stsm_section = False
    current_stsm = []

    for line in lines:
        if 'STSM' in line or 'Short Term Scientific Mission' in line:
            in_stsm_section = True
        if in_stsm_section:
            current_stsm.append(line)
            if line.strip() == '' and len(current_stsm) > 3:
                stsms.append('\n'.join(current_stsm))
                current_stsm = []

    return stsms


def extract_vmgs(text):
    """Extract VMG (Virtual Mobility Grant) information."""
    vmgs = []

    lines = text.split('\n')
    in_vmg_section = False
    current_vmg = []

    for line in lines:
        if 'VMG' in line or 'Virtual Mobility' in line:
            in_vmg_section = True
        if in_vmg_section:
            current_vmg.append(line)
            if line.strip() == '' and len(current_vmg) > 3:
                vmgs.append('\n'.join(current_vmg))
                current_vmg = []

    return vmgs


# Read all source documents
print("Reading source documents...")
action_chair = read_file('MidTermReport/CA19130_PR2_ActionChairReport_2024-06-27 (1).txt')
public_report = read_file('MidTermReport/CA19130_SecondProgressReportPublic_2024-06-27 (1).txt')
rapporteur = read_file('MidTermReport/CA19130_PR2_RapporteurReview_2024-06-27 (2).txt')

print(f"Action Chair Report: {len(action_chair)} chars")
print(f"Public Progress Report: {len(public_report)} chars")
print(f"Rapporteur Review: {len(rapporteur)} chars")

# Extract key sections from Public Report
print("\n=== Extracting from Public Progress Report ===")

# Find all events/conferences mentioned
events = extract_meetings_and_events(public_report)
print(f"Found {len(events)} event mentions")

# Find STSMs
stsms = extract_stsms(public_report)
print(f"Found {len(stsms)} STSM entries")

# Find VMGs
vmgs = extract_vmgs(public_report)
print(f"Found {len(vmgs)} VMG entries")

print("\nDone extracting data. Generating HTML reports...")

# Save extracted data for reference
output = []
output.append("=== EVENTS AND CONFERENCES ===\n")
for e in events[:50]:  # First 50
    output.append(e['line'])
    output.append("-" * 40)

output.append("\n\n=== STSMs ===\n")
for s in stsms[:20]:
    output.append(s)
    output.append("-" * 40)

output.append("\n\n=== VMGs ===\n")
for v in vmgs[:20]:
    output.append(v)
    output.append("-" * 40)

Path('extracted_data_summary.txt').write_text('\n'.join(output), encoding='utf-8')
print("Saved extracted_data_summary.txt")
