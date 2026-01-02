"""
Comprehensive extraction script for COST Action CA19130 Reports.
Extracts ALL content from Final Report and Mid-Term Report TXT files into JSON.

FIXES APPLIED (2026-01-02):
- Bug 1: WG Leaders extraction handles multi-line WG titles
- Bug 2: Other positions extraction handles Representative + multi-line names
- Bug 3: clean_page_markers() removes all page boundary artifacts
- Bug 4: Publications extraction uses DOI-based approach (captures all 199)
- Bug 5: Proof text cleaned of page markers
"""

import json
import re
from pathlib import Path
from datetime import datetime


def clean_page_markers(text):
    """Remove page markers and DRAFT watermarks from text.

    This is a critical utility function that cleans extracted text
    from PDF-to-TXT conversion artifacts.
    """
    if not text:
        return ""
    # Remove "--- Page X ---" followed by optional DRAFT
    text = re.sub(r'\n*--- Page \d+ ---\n*(?:DRAFT\n*)?', ' ', text)
    # Remove standalone DRAFT markers
    text = re.sub(r'\bDRAFT\b', '', text)
    # Remove standalone page numbers at line boundaries
    text = re.sub(r'\n\d+\n', '\n', text)
    # Clean up excessive whitespace
    text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces/tabs to single space
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Multiple newlines to double
    text = text.strip()
    return text


def split_into_pages(text):
    """Split text by page markers."""
    pages = {}
    pattern = r'--- Page (\d+) ---'
    parts = re.split(pattern, text)

    # parts[0] is before first page, parts[1] is page num, parts[2] is content, etc.
    for i in range(1, len(parts), 2):
        if i + 1 < len(parts):
            page_num = int(parts[i])
            content = parts[i + 1].strip()
            # Remove DRAFT watermarks
            content = re.sub(r'^DRAFT\s*\n', '', content)
            pages[page_num] = content
    return pages


def extract_leadership(pages):
    """Extract leadership positions from pages 2-3.

    FIXED: Now handles multi-line WG titles and other position names.
    """
    leadership = {
        "chair": None,
        "vice_chair": None,
        "wg_leaders": [],
        "other_positions": []
    }

    page2 = pages.get(2, "")

    # Extract Chair
    chair_match = re.search(r'Chair\n(Prof|Dr)\s+([^\n]+)\n([^\n]+@[^\n]+)\n([^\n]*)\n\s*(\w+)', page2)
    if chair_match:
        leadership["chair"] = {
            "title": chair_match.group(1),
            "name": chair_match.group(1) + " " + chair_match.group(2),
            "email": chair_match.group(3),
            "phone": chair_match.group(4) if chair_match.group(4) else "",
            "country": chair_match.group(5).strip()
        }

    # Extract Vice Chair
    vc_match = re.search(r'Action Vice-\s*Chair\n(Prof|Dr)\s+([^\n]+)\n([^\n]+@[^\n]+)\n([^\n]*)\n\s*(\w+)', page2)
    if vc_match:
        leadership["vice_chair"] = {
            "title": vc_match.group(1),
            "name": vc_match.group(1) + " " + vc_match.group(2),
            "email": vc_match.group(3),
            "phone": vc_match.group(4) if vc_match.group(4) else "",
            "country": vc_match.group(5).strip()
        }

    # Extract WG Leaders - FIXED for multi-line titles
    # Find the Working groups section
    wg_section_match = re.search(r'Working groups\n(.*?)(?:Other key leadership|$)', page2, re.DOTALL)
    if wg_section_match:
        wg_text = wg_section_match.group(1)

        # Split by WG numbers (1, 2, 3) at start of lines
        # Pattern: number at start, then multi-line title, then participant count, then leader info
        wg_blocks = re.split(r'\n(?=\d\n)', wg_text)

        for block in wg_blocks:
            block = block.strip()
            if not block or not block[0].isdigit():
                continue

            # Parse WG block: number\n<title lines>\n<participant count>\n<leader info>
            lines = block.split('\n')
            if len(lines) < 4:
                continue

            wg_num = int(lines[0])

            # Find participant count (3-digit number on its own line)
            participant_idx = -1
            for i, line in enumerate(lines[1:], 1):
                if re.match(r'^\d{2,3}$', line.strip()):
                    participant_idx = i
                    break

            if participant_idx == -1:
                continue

            # Title is everything between number and participant count
            wg_title = ' '.join(lines[1:participant_idx]).strip()
            participants = int(lines[participant_idx])

            # Find leader info (Prof/Dr followed by name, email, country)
            remaining = '\n'.join(lines[participant_idx+1:])
            leader_match = re.search(r'(Prof|Dr)\s+([^\n]+)\n([^\n]+@[^\n]+)\n\s*(\w+)', remaining)

            if leader_match:
                leadership["wg_leaders"].append({
                    "wg_number": wg_num,
                    "wg_title": wg_title,
                    "participants": participants,
                    "name": leader_match.group(1) + " " + leader_match.group(2),
                    "email": leader_match.group(3),
                    "country": leader_match.group(4).strip()
                })

    # Extract other positions - FIXED for multi-line position names and person names
    other_match = re.search(r'Other key leadership positions\n.*?Country\*\n(.*?)(?:\s*\*\s*The country|$)', page2, re.DOTALL)
    if other_match:
        other_text = other_match.group(1)

        # Split into position blocks by looking for known position types
        # Positions: Science Communication Coordinator, GH Scientific Representative

        # Pattern 1: Science Communication Coordinator
        scc_match = re.search(
            r'Science\s*\n?\s*Communication\s*\n?\s*Coordinator\s*\n(Dr|Prof)?\s*([^\n]+)\n([^\n]+@[^\n]+)\n(\w+)',
            other_text,
            re.IGNORECASE
        )
        if scc_match:
            title = scc_match.group(1) if scc_match.group(1) else ""
            name = (title + " " if title else "") + scc_match.group(2).strip()
            leadership["other_positions"].append({
                "position": "Science Communication Coordinator",
                "name": name,
                "email": scc_match.group(3).strip(),
                "country": scc_match.group(4).strip()
            })

        # Pattern 2: GH Scientific Representative (multi-line name)
        ghr_match = re.search(
            r'GH\s+Scientific\s*\n?\s*Representative\s*\n([^\n@]+(?:\n[^\n@]+)?)\n([^\n]+@[^\n]+)\n(\w+)',
            other_text,
            re.IGNORECASE
        )
        if ghr_match:
            # Name might be on multiple lines
            name_parts = ghr_match.group(1).strip().replace('\n', ' ')
            leadership["other_positions"].append({
                "position": "GH Scientific Representative",
                "name": name_parts,
                "email": ghr_match.group(2).strip(),
                "country": ghr_match.group(3).strip()
            })

    return leadership


def extract_participants(pages):
    """Extract participating countries from page 3."""
    page3 = pages.get(3, "")

    countries = []
    # Pattern: Country code followed by date
    country_pattern = r'\b([A-Z]{2})\n(\d{2}/\d{2}/\d{4})'
    for match in re.finditer(country_pattern, page3):
        countries.append({
            "code": match.group(1),
            "date": match.group(2)
        })

    return {
        "countries": countries,
        "total_countries": len(countries)
    }


def extract_summary(pages, is_final=True):
    """Extract summary section from page 4."""
    page4 = pages.get(4, "")

    summary = {
        "main_objective": "",
        "description": "",
        "website": "",
        "stats": {}
    }

    # Extract main objective
    obj_match = re.search(r'Main aim/ objective\n(.*?)(?:The Action addressed|During its first)', page4, re.DOTALL)
    if obj_match:
        summary["main_objective"] = clean_page_markers(obj_match.group(1))

    # Extract description (everything after "described below")
    desc_match = re.search(r'described below\n(.*?)(?:Action website|$)', page4, re.DOTALL)
    if desc_match:
        summary["description"] = clean_page_markers(desc_match.group(1))

    # Extract website
    web_match = re.search(r'https?://[^\s]+', page4)
    if web_match:
        summary["website"] = web_match.group(0)

    # Extract stats from description
    researchers_match = re.search(r'(\d+)\s+interdisciplinary researchers', page4)
    countries_match = re.search(r'from (\d+) countries', page4)
    cost_countries_match = re.search(r'(\d+) of those countries being European COST countries', page4)
    conferences_match = re.search(r'organized (\d+) research conferences', page4)
    participants_match = re.search(r'more than ([\d,]+) participants', page4)
    citations_match = re.search(r'cited more than ([\d,]+) times', page4)

    if researchers_match:
        summary["stats"]["researchers"] = int(researchers_match.group(1))
    if countries_match:
        summary["stats"]["countries"] = int(countries_match.group(1))
    if cost_countries_match:
        summary["stats"]["cost_countries"] = int(cost_countries_match.group(1))
    if conferences_match:
        summary["stats"]["conferences"] = int(conferences_match.group(1))
    if participants_match:
        summary["stats"]["participants"] = int(participants_match.group(1).replace(',', ''))
    if citations_match:
        summary["stats"]["citations"] = int(citations_match.group(1).replace(',', ''))

    return summary


def extract_objectives(full_text, pages):
    """Extract all 16 MoU objectives with FULL text.

    FIXED: Applies clean_page_markers() to all extracted text.
    """
    objectives = []

    # Find all objectives using pattern matching
    # Each objective starts with "Mou objective" and includes title, type, level, dependence, proof

    # Split text into objective blocks
    obj_pattern = r'Mou objective\n(.*?)(?=Mou objective\n|Deliverables\n|$)'
    matches = re.findall(obj_pattern, full_text, re.DOTALL)

    for i, match in enumerate(matches, 1):
        obj_text = match.strip()

        objective = {
            "number": i,
            "title": "",
            "type": [],
            "achievement": "",
            "dependence": "",
            "proof_text": ""
        }

        # Extract title (first paragraph before "Type of objective")
        title_match = re.search(r'^(.*?)(?:Type of objective)', obj_text, re.DOTALL)
        if title_match:
            objective["title"] = clean_page_markers(title_match.group(1))

        # Extract types
        type_pattern = r'(\d\.[a-z])\s+[A-Z][^1-9]*'
        types = re.findall(type_pattern, obj_text)
        objective["type"] = list(set(types))

        # Extract achievement level
        if "76 - 100%" in obj_text or "76-100%" in obj_text:
            objective["achievement"] = "76-100%"
        elif "51 - 75%" in obj_text or "51-75%" in obj_text:
            objective["achievement"] = "51-75%"
        elif "26 - 50%" in obj_text or "26-50%" in obj_text:
            objective["achievement"] = "26-50%"
        elif "0 - 25%" in obj_text or "0-25%" in obj_text:
            objective["achievement"] = "0-25%"

        # Extract dependence
        if "High" in obj_text:
            objective["dependence"] = "High"
        elif "Medium" in obj_text:
            objective["dependence"] = "Medium"
        elif "Low" in obj_text:
            objective["dependence"] = "Low"

        # Extract proof text (everything after "Proof of achievement" or "Description of progress")
        proof_match = re.search(r'(?:Proof of achievement of MoU\s*objective|Description of progress with\s*achieving the MoU objective)\n(.*?)$', obj_text, re.DOTALL)
        if proof_match:
            proof_text = proof_match.group(1).strip()
            # FIXED: Apply page marker cleanup
            objective["proof_text"] = clean_page_markers(proof_text)

        objectives.append(objective)

    return objectives


def extract_deliverables(full_text):
    """Extract all deliverables."""
    deliverables = []

    # Find deliverables section
    deliv_section = re.search(r'Deliverables\n.*?(?:Additional outputs|Co-authored Action publications)', full_text, re.DOTALL)
    if not deliv_section:
        return deliverables

    deliv_text = deliv_section.group(0)

    # Split by "Deliverable\n"
    deliv_pattern = r'Deliverable\n(.*?)(?=Deliverable\n|Additional outputs|Co-authored|$)'
    matches = re.findall(deliv_pattern, deliv_text, re.DOTALL)

    for i, match in enumerate(matches, 1):
        d_text = match.strip()

        deliverable = {
            "number": i,
            "title": "",
            "status": "",
            "dependence": "",
            "proof_url": ""
        }

        # Extract title (first part before "Level of achievement")
        title_match = re.search(r'^(.*?)(?:Level of achievement)', d_text, re.DOTALL)
        if title_match:
            deliverable["title"] = clean_page_markers(title_match.group(1))

        # Extract status
        if "Delivered" in d_text:
            deliverable["status"] = "Delivered"
        elif "Not delivered" in d_text:
            deliverable["status"] = "Not delivered"

        # Extract dependence
        if "High" in d_text:
            deliverable["dependence"] = "High"
        elif "Medium" in d_text:
            deliverable["dependence"] = "Medium"

        # Extract proof URL
        url_match = re.search(r'https?://[^\s]+', d_text)
        if url_match:
            deliverable["proof_url"] = url_match.group(0)

        deliverables.append(deliverable)

    return deliverables


def extract_publications(full_text):
    """Extract all publications with DOIs.

    FIXED: Uses DOI-based extraction that handles:
    - Split publication numbers (e.g., "10\n0" for 100)
    - Format changes (Title: vs Title\n)
    - Page boundaries
    """
    publications = []

    # Find publications section - ends at "Projects resulting from Action"
    pub_section = re.search(
        r'Co-authored Action publications.*?(?=Projects resulting from Action|Other Action results|$)',
        full_text,
        re.DOTALL
    )
    if not pub_section:
        # Try alternative pattern
        pub_section = re.search(
            r'Bibliographic data.*?(?=Projects resulting from Action|Other Action results|Please describe how|$)',
            full_text,
            re.DOTALL
        )

    if not pub_section:
        return publications

    pub_text = pub_section.group(0)

    # Find ALL DOIs in the publication section
    # DOI pattern: doi:10.XXXX/YYYY (various formats)
    doi_pattern = r'doi:(10\.\d{4,}/[^\s\n]+)'

    # Find all unique DOIs with their positions
    doi_matches = list(re.finditer(doi_pattern, pub_text))

    # Remove duplicate DOIs (same DOI appears twice per publication)
    seen_dois = set()
    unique_doi_positions = []
    for match in doi_matches:
        doi = match.group(1)
        if doi not in seen_dois:
            seen_dois.add(doi)
            unique_doi_positions.append((match.start(), doi))

    # For each unique DOI, extract publication details
    for idx, (pos, doi) in enumerate(unique_doi_positions):
        # Get context around this DOI (before and after)
        start = max(0, pos - 500)
        end = min(len(pub_text), pos + 2000)
        context = pub_text[start:end]

        publication = {
            "number": idx + 1,  # Sequential numbering
            "doi": f"doi:{doi}",
            "title": "",
            "authors": "",
            "type": "",
            "published_in": "",
            "countries": [],
            "peer_reviewed": False,
            "open_access": False
        }

        # Extract title - two formats:
        # Format 1: Title\n<text>
        # Format 2: Title: <text> or Title:<text>
        title_match = re.search(r'Title[:\n]\s*([^\n]+(?:\n[^A-Z\d][^\n]*)?)', context)
        if title_match:
            title = title_match.group(1).replace('\n', ' ').strip()
            # Clean up title
            title = re.sub(r'^Title[:\s]*', '', title)
            publication["title"] = clean_page_markers(title)

        # Extract authors - two formats
        author_match = re.search(r'Authors?[:\n]\s*([^\n]+(?:;\s*[^\n]+)*)', context)
        if author_match:
            authors = author_match.group(1).strip()
            # Clean up authors
            authors = re.sub(r'^Authors?[:\s]*', '', authors)
            publication["authors"] = clean_page_markers(authors)

        # Extract type
        type_match = re.search(r'Type\n([^\n]+)', context)
        if type_match:
            publication["type"] = type_match.group(1).strip()

        # Extract published in
        pub_in_match = re.search(r'Published in\n([^\n]+)', context)
        if not pub_in_match:
            # Try alternative format
            pub_in_match = re.search(r'Title of the periodical:\s*([^\n]+)', context)
        if pub_in_match:
            publication["published_in"] = pub_in_match.group(1).strip()

        # Extract countries (2-letter codes)
        countries_match = re.search(r'\n([A-Z]{2}(?:,\s*[A-Z]{2})*)\n', context)
        if countries_match:
            publication["countries"] = [c.strip() for c in countries_match.group(1).split(',')]

        # Check peer reviewed and open access
        # Look for Y in appropriate context
        if re.search(r'\nY\nY\nY\n', context):
            publication["peer_reviewed"] = True
            publication["open_access"] = True
        elif re.search(r'\nY\n', context):
            publication["peer_reviewed"] = True

        publications.append(publication)

    return publications


def extract_stsms_and_vmgs(full_text):
    """Extract STSM and VMG information."""
    stsms = []
    vmgs = []

    # Find STSM section
    stsm_match = re.search(r'STSM.*?grant.*?program.*?(.*?)(?:VMG|Virtual Mobility|$)', full_text, re.DOTALL | re.IGNORECASE)
    if stsm_match:
        stsm_text = stsm_match.group(0)
        # Extract key info about STSMs
        stsms.append({
            "description": clean_page_markers(stsm_text[:2000]),
            "key_activities": []
        })

        # Find specific STSM mentions
        stsm_names = re.findall(r'led by ([A-Z][a-z]+ [A-Z][a-z]+)', stsm_text)
        for name in stsm_names:
            stsms[0]["key_activities"].append({"researcher": name})

    # Find VMG section
    vmg_match = re.search(r'(?:VMG|Virtual Mobility Grant[s]?).*?(.*?)(?:Please describe how|$)', full_text, re.DOTALL | re.IGNORECASE)
    if vmg_match:
        vmg_text = vmg_match.group(0)

        # Extract VMG mentions by name
        vmg_pattern = r"(\w+)'s VMG\s+([^.]+\.)"
        for m in re.finditer(vmg_pattern, vmg_text):
            vmgs.append({
                "researcher": m.group(1),
                "description": m.group(2).strip()
            })

    return {"stsms": stsms, "vmgs": vmgs}


def extract_impacts(full_text):
    """Extract career impacts and other achievements."""
    impacts = {
        "career_benefits": "",
        "experience_level": "",
        "stakeholder_engagement": "",
        "dissemination_approach": ""
    }

    # Career benefits
    career_match = re.search(r'careers, skills and network.*?(.*?)(?:career benefits were mainly|$)', full_text, re.DOTALL)
    if career_match:
        impacts["career_benefits"] = clean_page_markers(career_match.group(1)[:2000])

    # Experience level
    exp_match = re.search(r'career benefits were mainly to researchers.*?(\d+\s*years)', full_text)
    if exp_match:
        impacts["experience_level"] = exp_match.group(1)

    # Stakeholder engagement
    stake_match = re.search(r'stakeholders.*?engaged and how\?.*?(.*?)(?:\d+\n\n|$)', full_text, re.DOTALL)
    if stake_match:
        impacts["stakeholder_engagement"] = clean_page_markers(stake_match.group(1)[:2000])

    # Dissemination approach
    dissem_match = re.search(r'Dissemination and exploitation approach.*?\n(.*?)(?:Dissemination meetings|$)', full_text, re.DOTALL)
    if dissem_match:
        impacts["dissemination_approach"] = clean_page_markers(dissem_match.group(1)[:2000])

    return impacts


def extract_meetings_and_events(full_text):
    """Extract meetings, conferences, and events."""
    events = []

    # Find dissemination activities section
    dissem_match = re.search(r'Other dissemination activities.*?(.*?)(?:Exploitation|$)', full_text, re.DOTALL)
    if not dissem_match:
        return events

    dissem_text = dissem_match.group(0)

    # Extract events with URLs
    event_pattern = r'((?:Organizing|Organisation|Workshop|Conference|The).*?)\n.*?Target audience.*?\n(.*?)\n.*?(?:Outcome|Result).*?\n(.*?)\n.*?(https?://[^\s]+)'

    for match in re.finditer(event_pattern, dissem_text, re.DOTALL):
        events.append({
            "title": clean_page_markers(match.group(1)[:200]),
            "target_audience": clean_page_markers(match.group(2)[:200]),
            "outcome": clean_page_markers(match.group(3)[:500]),
            "url": match.group(4).strip()
        })

    # Also find URLs with names
    url_events = re.findall(r'(https?://[^\s]+)\s+', dissem_text)
    for url in url_events[:20]:  # Limit to 20
        if url not in [e.get("url", "") for e in events]:
            events.append({"url": url})

    return events


def parse_report(txt_path, is_final=True):
    """Parse a complete report TXT file and return structured JSON."""
    with open(txt_path, 'r', encoding='utf-8') as f:
        full_text = f.read()

    pages = split_into_pages(full_text)

    # Determine report type from content
    if "Final Achievement Report" in full_text:
        report_type = "Final Achievement Report"
        period = "14/09/2020 - 13/09/2024"
    else:
        report_type = "Progress Report at 24 months"
        period = "14/09/2020 - 14/09/2022"

    # Build complete report structure
    report = {
        "metadata": {
            "title": report_type,
            "action_code": "CA19130",
            "action_name": "Fintech and Artificial Intelligence in Finance - Towards a transparent financial industry",
            "period": period,
            "pages": len(pages),
            "generated": datetime.now().strftime("%Y-%m-%d"),
            "source_file": str(txt_path)
        },
        "summary": extract_summary(pages, is_final),
        "leadership": extract_leadership(pages),
        "participants": extract_participants(pages),
        "objectives": extract_objectives(full_text, pages),
        "deliverables": extract_deliverables(full_text),
        "publications": extract_publications(full_text),
        "stsms_vmgs": extract_stsms_and_vmgs(full_text),
        "impacts": extract_impacts(full_text),
        "events": extract_meetings_and_events(full_text),
        "raw_pages": {}  # Store raw page content for full display
    }

    # Store raw pages for complete display
    for page_num, content in pages.items():
        report["raw_pages"][str(page_num)] = content

    return report


def create_comparison(final_report, midterm_report):
    """Create a comparison structure between Final and Mid-Term reports."""
    comparison = {
        "metadata": {
            "generated": datetime.now().strftime("%Y-%m-%d"),
            "final_report": final_report["metadata"],
            "midterm_report": midterm_report["metadata"]
        },
        "summary_comparison": {
            "researchers": {
                "midterm": midterm_report["summary"]["stats"].get("researchers", 0),
                "final": final_report["summary"]["stats"].get("researchers", 0),
                "change": final_report["summary"]["stats"].get("researchers", 0) - midterm_report["summary"]["stats"].get("researchers", 0)
            },
            "countries": {
                "midterm": midterm_report["summary"]["stats"].get("countries", 0),
                "final": final_report["summary"]["stats"].get("countries", 0),
                "change": final_report["summary"]["stats"].get("countries", 0) - midterm_report["summary"]["stats"].get("countries", 0)
            }
        },
        "objectives_comparison": [],
        "deliverables_comparison": [],
        "publications_comparison": {
            "midterm_count": len(midterm_report["publications"]),
            "final_count": len(final_report["publications"]),
            "new_publications": len(final_report["publications"]) - len(midterm_report["publications"])
        }
    }

    # Compare objectives
    final_objectives = {obj["number"]: obj for obj in final_report["objectives"]}
    midterm_objectives = {obj["number"]: obj for obj in midterm_report["objectives"]}

    all_obj_nums = set(final_objectives.keys()) | set(midterm_objectives.keys())

    for num in sorted(all_obj_nums):
        final_obj = final_objectives.get(num, {})
        midterm_obj = midterm_objectives.get(num, {})

        comparison["objectives_comparison"].append({
            "number": num,
            "title": final_obj.get("title", midterm_obj.get("title", "")),
            "midterm_achievement": midterm_obj.get("achievement", "N/A"),
            "final_achievement": final_obj.get("achievement", "N/A"),
            "midterm_proof": midterm_obj.get("proof_text", ""),
            "final_proof": final_obj.get("proof_text", ""),
            "achievement_changed": midterm_obj.get("achievement", "") != final_obj.get("achievement", "")
        })

    # Compare deliverables
    final_deliverables = {d["number"]: d for d in final_report["deliverables"]}
    midterm_deliverables = {d["number"]: d for d in midterm_report["deliverables"]}

    all_deliv_nums = set(final_deliverables.keys()) | set(midterm_deliverables.keys())

    for num in sorted(all_deliv_nums):
        final_d = final_deliverables.get(num, {})
        midterm_d = midterm_deliverables.get(num, {})

        comparison["deliverables_comparison"].append({
            "number": num,
            "title": final_d.get("title", midterm_d.get("title", "")),
            "midterm_status": midterm_d.get("status", "N/A"),
            "final_status": final_d.get("status", "N/A"),
            "status_changed": midterm_d.get("status", "") != final_d.get("status", "")
        })

    return comparison


def main():
    """Main extraction function."""
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / "data"
    data_dir.mkdir(exist_ok=True)

    # File paths
    final_txt = base_dir / "FinalReport_in_progress" / "CA19130_FA_ActionChairReport_2026-01-02.txt"
    midterm_txt = base_dir / "MidTermReport" / "CA19130_PR2_ActionChairReport_2024-06-27 (1).txt"

    print("=" * 60)
    print("COST Action CA19130 Report Extraction")
    print("=" * 60)

    # Extract Final Report
    print(f"\n[1/3] Extracting Final Report from: {final_txt.name}")
    final_report = parse_report(final_txt, is_final=True)
    final_json_path = data_dir / "final_report_full.json"
    with open(final_json_path, 'w', encoding='utf-8') as f:
        json.dump(final_report, f, indent=2, ensure_ascii=False)
    print(f"  -> Saved: {final_json_path}")
    print(f"  -> Pages: {final_report['metadata']['pages']}")
    print(f"  -> Objectives: {len(final_report['objectives'])}")
    print(f"  -> Deliverables: {len(final_report['deliverables'])}")
    print(f"  -> Publications: {len(final_report['publications'])}")
    print(f"  -> WG Leaders: {len(final_report['leadership']['wg_leaders'])}")
    print(f"  -> Other Positions: {len(final_report['leadership']['other_positions'])}")

    # Extract Mid-Term Report
    print(f"\n[2/3] Extracting Mid-Term Report from: {midterm_txt.name}")
    midterm_report = parse_report(midterm_txt, is_final=False)
    midterm_json_path = data_dir / "midterm_report_full.json"
    with open(midterm_json_path, 'w', encoding='utf-8') as f:
        json.dump(midterm_report, f, indent=2, ensure_ascii=False)
    print(f"  -> Saved: {midterm_json_path}")
    print(f"  -> Pages: {midterm_report['metadata']['pages']}")
    print(f"  -> Objectives: {len(midterm_report['objectives'])}")
    print(f"  -> Deliverables: {len(midterm_report['deliverables'])}")
    print(f"  -> Publications: {len(midterm_report['publications'])}")
    print(f"  -> WG Leaders: {len(midterm_report['leadership']['wg_leaders'])}")
    print(f"  -> Other Positions: {len(midterm_report['leadership']['other_positions'])}")

    # Create Comparison
    print(f"\n[3/3] Creating comparison...")
    comparison = create_comparison(final_report, midterm_report)
    comparison_json_path = data_dir / "report_comparison.json"
    with open(comparison_json_path, 'w', encoding='utf-8') as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)
    print(f"  -> Saved: {comparison_json_path}")
    print(f"  -> Objectives compared: {len(comparison['objectives_comparison'])}")
    print(f"  -> Deliverables compared: {len(comparison['deliverables_comparison'])}")

    print("\n" + "=" * 60)
    print("Extraction Complete!")
    print("=" * 60)

    return final_report, midterm_report, comparison


if __name__ == "__main__":
    main()
