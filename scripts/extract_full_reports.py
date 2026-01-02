"""
Comprehensive extraction script for COST Action CA19130 Reports.
Extracts ALL content from Final Report and Mid-Term Report TXT files into JSON.
"""

import json
import re
from pathlib import Path
from datetime import datetime


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
    """Extract leadership positions from pages 2-3."""
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

    # Extract WG Leaders
    wg_pattern = r'(\d)\n([^\n]+)\n(\d+)\n(Prof|Dr)\s+([^\n]+)\n([^\n]+@[^\n]+)\n\s*(\w+)'
    for match in re.finditer(wg_pattern, page2):
        leadership["wg_leaders"].append({
            "wg_number": int(match.group(1)),
            "wg_title": match.group(2),
            "participants": int(match.group(3)),
            "name": match.group(4) + " " + match.group(5),
            "email": match.group(6),
            "country": match.group(7).strip()
        })

    # Extract other positions
    other_match = re.search(r'Other key leadership positions.*?Country\*\n(.*?)(?:\*|$)', page2, re.DOTALL)
    if other_match:
        other_text = other_match.group(1)
        # Parse Science Communication Coordinator and GH Scientific Representative
        pos_pattern = r'(\w+(?:\s+\w+)*)\nCoordinator\n(Dr|Prof)?\s*([^\n]+)\n([^\n]+@[^\n]+)\n(\w+)'
        for m in re.finditer(pos_pattern, other_text):
            leadership["other_positions"].append({
                "position": m.group(1) + " Coordinator",
                "name": (m.group(2) + " " if m.group(2) else "") + m.group(3),
                "email": m.group(4),
                "country": m.group(5)
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
        summary["main_objective"] = obj_match.group(1).strip()

    # Extract description (everything after "described below")
    desc_match = re.search(r'described below\n(.*?)(?:Action website|$)', page4, re.DOTALL)
    if desc_match:
        summary["description"] = desc_match.group(1).strip()

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
    """Extract all 16 MoU objectives with FULL text."""
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
            objective["title"] = title_match.group(1).strip()

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
            # Clean up page numbers
            proof_text = re.sub(r'\n\d+\n', '\n', proof_text)
            objective["proof_text"] = proof_text

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
            deliverable["title"] = title_match.group(1).strip()

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
    """Extract all publications with DOIs."""
    publications = []

    # Find publications section
    pub_section = re.search(r'Co-authored Action publications.*?(?:Other Action results|Additional achievements|Dissemination and exploitation|$)', full_text, re.DOTALL)
    if not pub_section:
        # Try alternative pattern
        pub_section = re.search(r'Bibliographic data.*?(?:Other Action results|Please describe how|$)', full_text, re.DOTALL)

    if not pub_section:
        return publications

    pub_text = pub_section.group(0)

    # Find each publication by DOI pattern
    pub_pattern = r'(\d+)\n(doi:[^\n]+)\nTitle\n([^\n]+(?:\n[^\n]+)?)\n(?:Author[s]?\n([^\n]+(?:\n[^\n]+)?))?\nDOI\n[^\n]+\nType\n([^\n]+)'

    # Simpler approach: find all DOIs and extract surrounding context
    doi_pattern = r'(\d+)\n(doi:[\d\./\w-]+)'

    for match in re.finditer(doi_pattern, pub_text):
        pub_num = int(match.group(1))
        doi = match.group(2)

        # Get text around this match for more details
        start = match.start()
        end = min(start + 2000, len(pub_text))
        context = pub_text[start:end]

        publication = {
            "number": pub_num,
            "doi": doi,
            "title": "",
            "authors": "",
            "type": "",
            "published_in": "",
            "countries": [],
            "peer_reviewed": False,
            "open_access": False
        }

        # Extract title
        title_match = re.search(r'Title\n([^\n]+(?:\n[^A-Z][^\n]*)?)', context)
        if title_match:
            publication["title"] = title_match.group(1).replace('\n', ' ').strip()

        # Extract authors
        author_match = re.search(r'Author[s]?\n([^\n]+(?:;\s*[^\n]+)*)', context)
        if author_match:
            publication["authors"] = author_match.group(1).strip()

        # Extract type
        type_match = re.search(r'Type\n([^\n]+)', context)
        if type_match:
            publication["type"] = type_match.group(1).strip()

        # Extract published in
        pub_in_match = re.search(r'Published in\n([^\n]+)', context)
        if pub_in_match:
            publication["published_in"] = pub_in_match.group(1).strip()

        # Extract countries
        countries_match = re.search(r'\n([A-Z]{2}(?:,\s*[A-Z]{2})*)\n', context)
        if countries_match:
            publication["countries"] = [c.strip() for c in countries_match.group(1).split(',')]

        # Check peer reviewed and open access (Y in those columns)
        if '\nY\n' in context:
            publication["peer_reviewed"] = True
            publication["open_access"] = True

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
            "description": stsm_text[:2000].strip(),
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
        impacts["career_benefits"] = career_match.group(1).strip()[:2000]

    # Experience level
    exp_match = re.search(r'career benefits were mainly to researchers.*?(\d+\s*years)', full_text)
    if exp_match:
        impacts["experience_level"] = exp_match.group(1)

    # Stakeholder engagement
    stake_match = re.search(r'stakeholders.*?engaged and how\?.*?(.*?)(?:\d+\n\n|$)', full_text, re.DOTALL)
    if stake_match:
        impacts["stakeholder_engagement"] = stake_match.group(1).strip()[:2000]

    # Dissemination approach
    dissem_match = re.search(r'Dissemination and exploitation approach.*?\n(.*?)(?:Dissemination meetings|$)', full_text, re.DOTALL)
    if dissem_match:
        impacts["dissemination_approach"] = dissem_match.group(1).strip()[:2000]

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
            "title": match.group(1).strip()[:200],
            "target_audience": match.group(2).strip()[:200],
            "outcome": match.group(3).strip()[:500],
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
