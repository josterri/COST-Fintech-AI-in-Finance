#!/usr/bin/env python3
"""
FFR Data Verification Script for COST Action CA19130
Cross-checks all JSON data against original FFR text files

This script:
1. Parses each FFR text file for official totals
2. Extracts meeting counts, STSM counts, VM counts, TS counts per GP
3. Extracts financial totals (Budget, Actuals, by category)
4. Compares against JSON data files
5. Generates verification report with PASS/FAIL for each metric
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SOURCE_DIR = Path(r"D:\Joerg\Research\slides\COST_Work_and_Budget_Plans\extracted_text")
REPORTS_DIR = PROJECT_ROOT / "reports"

# FFR file mapping
FFR_FILES = {
    1: "AGA-CA19130-1-FFR_ID2193.txt",
    2: "AGA-CA19130-2-FFR_ID2346.txt",
    3: "AGA-CA19130-3-FFR_ID2998.txt",
    4: "AGA-CA19130-4-FFR_ID3993.txt",
    5: "AGA-CA19130-5-FFR_ID4828.txt"
}

# GP date ranges
GP_DATES = {
    1: ("01/11/2020", "31/10/2021"),
    2: ("01/11/2021", "31/05/2022"),
    3: ("01/06/2022", "31/10/2022"),
    4: ("01/11/2022", "31/10/2023"),
    5: ("01/11/2023", "30/09/2024")
}


def parse_amount(text: str) -> float:
    """Parse EUR amount from text, handling various formats"""
    if not text:
        return 0.0
    # Remove EUR, spaces, and handle thousand separators
    text = re.sub(r'EUR|€', '', text).strip()
    text = text.replace(' ', '').replace(',', '')
    try:
        return float(text)
    except ValueError:
        return 0.0


def extract_ffr_data(gp: int) -> Dict[str, Any]:
    """Extract key data from an FFR text file"""
    ffr_file = SOURCE_DIR / FFR_FILES[gp]

    if not ffr_file.exists():
        return {"error": f"File not found: {ffr_file}"}

    content = ffr_file.read_text(encoding='utf-8')

    result = {
        "grant_period": gp,
        "source_file": FFR_FILES[gp],
        "budget": 0.0,
        "actual": 0.0,
        "meetings_expenditure": 0.0,
        "meetings_count": 0,
        "training_schools_expenditure": 0.0,
        "training_schools_count": 0,
        "stsm_expenditure": 0.0,
        "stsm_count": 0,
        "vm_expenditure": 0.0,
        "vm_count": 0,
        "itc_expenditure": 0.0,
        "dissemination_expenditure": 0.0,
        "oersa_expenditure": 0.0,
        "vns_expenditure": 0.0,
        "fsac_expenditure": 0.0,
        "los_grants": []
    }

    # Extract Grant Budget (handle amendments)
    budget_match = re.search(r'Total Grant Budget\s+EUR\s+([\d\s,\.]+)', content)
    if budget_match:
        result["budget"] = parse_amount(budget_match.group(1))
    else:
        budget_match = re.search(r'Grant Budget\s+([\d\s,\.]+)', content)
        if budget_match:
            result["budget"] = parse_amount(budget_match.group(1))

    # Extract Total Actual Expenditure
    actual_match = re.search(r'Total eligible expenditure.*?([\d\s,\.]+)\s+([\d\s,\.]+)\s+([\d\s,\.]+)\s+([\d\s,\.]+)', content)
    if actual_match:
        result["actual"] = parse_amount(actual_match.group(4))

    # Extract category expenditures from the summary table
    # Handle both old and new FFR formats

    # Meetings
    meetings_match = re.search(r'(?:Total\s+)?Meetings?\s+([\d\s,\.]+)\s+([\d\s,\.]+)\s+([\d\s,\.]+)\s+([\d\s,\.]+)', content)
    if meetings_match:
        result["meetings_expenditure"] = parse_amount(meetings_match.group(4))

    # Training Schools
    schools_match = re.search(r'(?:Total\s+)?(?:Training\s+)?Schools?\s+([\d\s,\.]+)\s+([\d\s,\.]+)\s+([\d\s,\.]+)\s+([\d\s,\.]+)', content)
    if schools_match:
        result["training_schools_expenditure"] = parse_amount(schools_match.group(4))

    # STSM - handle both naming conventions
    stsm_match = re.search(r'(?:Total\s+)?(?:Short[- ]Term\s+Scientific\s+Mission|STSM)\s+([\d\s,\.]+)\s+([\d\s,\.]+)\s+([\d\s,\.]+)\s+([\d\s,\.]+)', content, re.IGNORECASE)
    if stsm_match:
        result["stsm_expenditure"] = parse_amount(stsm_match.group(4))

    # Virtual Mobility
    vm_match = re.search(r'Virtual\s+(?:Mobility|Networking\s+Tool)\s+([\d\s,\.]+)\s+([\d\s,\.]+)\s+([\d\s,\.]+)\s+([\d\s,\.]+)', content, re.IGNORECASE)
    if vm_match:
        result["vm_expenditure"] = parse_amount(vm_match.group(4))

    # ITC Conference Grants
    itc_match = re.search(r'(?:Total\s+)?ITC\s+Conference\s+(?:Grants?)?\s+([\d\s,\.]+)\s+([\d\s,\.]+)\s+([\d\s,\.]+)\s+([\d\s,\.]+)', content, re.IGNORECASE)
    if itc_match:
        result["itc_expenditure"] = parse_amount(itc_match.group(4))

    # FSAC
    fsac_match = re.search(r'FSAC\s+\(max\s+15%\)\s+([\d\s,\.]+)\s+([\d\s,\.]+)\s+([\d\s,\.]+)\s+([\d\s,\.]+)', content)
    if fsac_match:
        result["fsac_expenditure"] = parse_amount(fsac_match.group(4))

    # OERSA
    oersa_match = re.search(r'(?:Total\s+)?OERSA\s+([\d\s,\.]+)\s+([\d\s,\.]+)\s+([\d\s,\.]+)\s+([\d\s,\.]+)', content)
    if oersa_match:
        result["oersa_expenditure"] = parse_amount(oersa_match.group(4))

    # Dissemination
    dissem_match = re.search(r'(?:Total\s+)?(?:Action\s+)?Dissemination.*?([\d\s,\.]+)\s+([\d\s,\.]+)\s+([\d\s,\.]+)\s+([\d\s,\.]+)', content)
    if dissem_match:
        result["dissemination_expenditure"] = parse_amount(dissem_match.group(4))

    # VNS (Virtual Networking Support)
    vns_match = re.search(r'Virtual\s+Networking\s+Support\s+([\d\s,\.]+)\s+([\d\s,\.]+)\s+([\d\s,\.]+)\s+([\d\s,\.]+)', content)
    if vns_match:
        result["vns_expenditure"] = parse_amount(vns_match.group(4))

    # Count meetings
    meeting_sections = re.findall(r'Meeting\s+(\d+)\s*\nStart\s+date', content)
    result["meetings_count"] = len(meeting_sections)

    # Count training schools
    ts_sections = re.findall(r'Training\s+School\s+(\d+)\s*\nStart\s+date', content)
    result["training_schools_count"] = len(ts_sections)

    # Count STSMs from list
    stsm_list_match = re.search(r'List of paid Short[- ]Term Scientific Mission.*?Sub-total actual amounts', content, re.DOTALL | re.IGNORECASE)
    if stsm_list_match:
        stsm_entries = re.findall(r'^\d+\s+(?:Dr|Mr|Ms|Prof)?\s*[\w\s\-]+\s+(?:Y|N)(?:ES|O)?', stsm_list_match.group(), re.MULTILINE)
        result["stsm_count"] = len(stsm_entries)

    # Count VM grants from list
    vm_list_match = re.search(r'List of paid Virtual (?:Mobility|Grants).*?Sub-total actual amounts', content, re.DOTALL | re.IGNORECASE)
    if vm_list_match:
        vm_entries = re.findall(r'^\d+\s+[\w\s\-]+\s+VM', vm_list_match.group(), re.MULTILINE)
        result["vm_count"] = len(vm_entries)

    # Extract LOS grants
    los_matches = re.findall(r'Local Organiser Support \(LOS\) Grant\s*\nSub-total actual amounts - Paid\s+([\d\s,\.]+)', content)
    result["los_grants"] = [parse_amount(m) for m in los_matches if parse_amount(m) > 0]

    return result


def load_json_data() -> Dict[str, Any]:
    """Load all relevant JSON data files"""
    data = {}

    json_files = [
        "meetings_participants.json",
        "stsm_detailed.json",
        "virtual_mobility_full.json",
        "training_school_attendees.json",
        "participant_master.json",
        "summary_statistics.json",
        "budget_summaries.json",
        "los_grants.json"
    ]

    for filename in json_files:
        filepath = DATA_DIR / filename
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                data[filename.replace('.json', '')] = json.load(f)
        else:
            data[filename.replace('.json', '')] = None
            print(f"Warning: {filename} not found")

    return data


def count_by_gp(data: List[Dict], gp_field: str = "grant_period") -> Dict[int, int]:
    """Count items by grant period"""
    counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for item in data:
        gp = item.get(gp_field, 0)
        if gp in counts:
            counts[gp] += 1
    return counts


def verify_data() -> Dict[str, Any]:
    """Main verification function"""
    print("=" * 60)
    print("FFR Data Verification - COST Action CA19130")
    print("=" * 60)
    print(f"Run time: {datetime.now().isoformat()}")
    print()

    results = {
        "timestamp": datetime.now().isoformat(),
        "ffr_data": {},
        "json_data": {},
        "comparisons": {},
        "summary": {
            "total_checks": 0,
            "passed": 0,
            "failed": 0,
            "warnings": 0
        }
    }

    # Extract FFR data
    print("Extracting data from FFR source files...")
    for gp in range(1, 6):
        print(f"  Processing FFR{gp} ({FFR_FILES[gp]})...")
        results["ffr_data"][f"GP{gp}"] = extract_ffr_data(gp)

    # Load JSON data
    print("\nLoading JSON data files...")
    json_data = load_json_data()
    results["json_data"] = {
        "meetings_count": len(json_data.get("meetings_participants", [])) if json_data.get("meetings_participants") else 0,
        "stsm_count": len(json_data.get("stsm_detailed", [])) if json_data.get("stsm_detailed") else 0,
        "vm_count": len(json_data.get("virtual_mobility_full", [])) if json_data.get("virtual_mobility_full") else 0,
        "ts_count": len(json_data.get("training_school_attendees", [])) if json_data.get("training_school_attendees") else 0,
        "participants_count": len(json_data.get("participant_master", [])) if json_data.get("participant_master") else 0
    }

    # Count by GP from JSON
    if json_data.get("meetings_participants"):
        results["json_data"]["meetings_by_gp"] = count_by_gp(json_data["meetings_participants"])
    if json_data.get("stsm_detailed"):
        results["json_data"]["stsm_by_gp"] = count_by_gp(json_data["stsm_detailed"])
    if json_data.get("virtual_mobility_full"):
        results["json_data"]["vm_by_gp"] = count_by_gp(json_data["virtual_mobility_full"])
    if json_data.get("training_school_attendees"):
        results["json_data"]["ts_by_gp"] = count_by_gp(json_data["training_school_attendees"])

    # Compare totals
    print("\n" + "=" * 60)
    print("VERIFICATION RESULTS")
    print("=" * 60)

    comparisons = []

    # Calculate FFR totals
    ffr_meetings = sum(results["ffr_data"][f"GP{gp}"].get("meetings_count", 0) for gp in range(1, 6))
    ffr_stsm = sum(results["ffr_data"][f"GP{gp}"].get("stsm_count", 0) for gp in range(1, 6))
    ffr_vm = sum(results["ffr_data"][f"GP{gp}"].get("vm_count", 0) for gp in range(1, 6))
    ffr_ts = sum(results["ffr_data"][f"GP{gp}"].get("training_schools_count", 0) for gp in range(1, 6))

    # Meetings comparison
    json_meetings = results["json_data"]["meetings_count"]
    match = ffr_meetings == json_meetings
    status = "PASS" if match else "FAIL"
    comparisons.append({
        "metric": "Total Meetings",
        "ffr_value": ffr_meetings,
        "json_value": json_meetings,
        "match": match,
        "status": status
    })
    print(f"\nTotal Meetings: FFR={ffr_meetings}, JSON={json_meetings} [{status}]")

    # STSMs comparison
    json_stsm = results["json_data"]["stsm_count"]
    match = ffr_stsm == json_stsm
    status = "PASS" if match else "FAIL"
    comparisons.append({
        "metric": "Total STSMs",
        "ffr_value": ffr_stsm,
        "json_value": json_stsm,
        "match": match,
        "status": status
    })
    print(f"Total STSMs: FFR={ffr_stsm}, JSON={json_stsm} [{status}]")

    # VM comparison
    json_vm = results["json_data"]["vm_count"]
    match = ffr_vm == json_vm
    status = "PASS" if match else "FAIL"
    comparisons.append({
        "metric": "Total VM Grants",
        "ffr_value": ffr_vm,
        "json_value": json_vm,
        "match": match,
        "status": status
    })
    print(f"Total VM Grants: FFR={ffr_vm}, JSON={json_vm} [{status}]")

    # Training Schools comparison
    json_ts = results["json_data"]["ts_count"]
    match = ffr_ts == json_ts
    status = "PASS" if match else "FAIL"
    comparisons.append({
        "metric": "Total Training Schools",
        "ffr_value": ffr_ts,
        "json_value": json_ts,
        "match": match,
        "status": status
    })
    print(f"Total Training Schools: FFR={ffr_ts}, JSON={json_ts} [{status}]")

    # Financial totals
    print("\n--- Financial Totals by Grant Period ---")
    total_budget = 0
    total_actual = 0

    for gp in range(1, 6):
        gp_data = results["ffr_data"][f"GP{gp}"]
        budget = gp_data.get("budget", 0)
        actual = gp_data.get("actual", 0)
        total_budget += budget
        total_actual += actual
        print(f"GP{gp}: Budget={budget:,.2f} EUR, Actual={actual:,.2f} EUR")

    print(f"\nGrand Total: Budget={total_budget:,.2f} EUR, Actual={total_actual:,.2f} EUR")

    results["comparisons"] = comparisons
    results["summary"]["total_checks"] = len(comparisons)
    results["summary"]["passed"] = sum(1 for c in comparisons if c["match"])
    results["summary"]["failed"] = sum(1 for c in comparisons if not c["match"])

    # Check against summary_statistics.json
    print("\n--- Checking summary_statistics.json ---")
    if json_data.get("summary_statistics"):
        ss = json_data["summary_statistics"]
        issues = []

        if ss.get("total_meetings") != json_meetings:
            issues.append(f"total_meetings: {ss.get('total_meetings')} should be {json_meetings}")
        if ss.get("total_stsms") != json_stsm:
            issues.append(f"total_stsms: {ss.get('total_stsms')} should be {json_stsm}")
        if ss.get("total_virtual_mobility") != json_vm:
            issues.append(f"total_virtual_mobility: {ss.get('total_virtual_mobility')} should be {json_vm}")
        if ss.get("total_training_schools") != json_ts:
            issues.append(f"total_training_schools: {ss.get('total_training_schools')} should be {json_ts}")

        if issues:
            print("ISSUES FOUND in summary_statistics.json:")
            for issue in issues:
                print(f"  - {issue}")
            results["summary"]["warnings"] += len(issues)
        else:
            print("summary_statistics.json is up to date")

    # Per-GP breakdown
    print("\n--- Meetings by Grant Period ---")
    json_meetings_by_gp = results["json_data"].get("meetings_by_gp", {})
    for gp in range(1, 6):
        ffr_count = results["ffr_data"][f"GP{gp}"].get("meetings_count", 0)
        json_count = json_meetings_by_gp.get(gp, 0)
        match_status = "OK" if ffr_count == json_count else "MISMATCH"
        print(f"  GP{gp}: FFR={ffr_count}, JSON={json_count} [{match_status}]")

    print("\n--- STSMs by Grant Period ---")
    json_stsm_by_gp = results["json_data"].get("stsm_by_gp", {})
    for gp in range(1, 6):
        ffr_count = results["ffr_data"][f"GP{gp}"].get("stsm_count", 0)
        json_count = json_stsm_by_gp.get(gp, 0)
        match_status = "OK" if ffr_count == json_count else "MISMATCH"
        print(f"  GP{gp}: FFR={ffr_count}, JSON={json_count} [{match_status}]")

    print("\n--- VM Grants by Grant Period ---")
    json_vm_by_gp = results["json_data"].get("vm_by_gp", {})
    for gp in range(1, 6):
        ffr_count = results["ffr_data"][f"GP{gp}"].get("vm_count", 0)
        json_count = json_vm_by_gp.get(gp, 0)
        match_status = "OK" if ffr_count == json_count else "MISMATCH"
        print(f"  GP{gp}: FFR={ffr_count}, JSON={json_count} [{match_status}]")

    print("\n--- Training Schools by Grant Period ---")
    json_ts_by_gp = results["json_data"].get("ts_by_gp", {})
    for gp in range(1, 6):
        ffr_count = results["ffr_data"][f"GP{gp}"].get("training_schools_count", 0)
        json_count = json_ts_by_gp.get(gp, 0)
        match_status = "OK" if ffr_count == json_count else "MISMATCH"
        print(f"  GP{gp}: FFR={ffr_count}, JSON={json_count} [{match_status}]")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total Checks: {results['summary']['total_checks']}")
    print(f"Passed: {results['summary']['passed']}")
    print(f"Failed: {results['summary']['failed']}")
    print(f"Warnings: {results['summary']['warnings']}")

    return results


def save_reports(results: Dict[str, Any]):
    """Save verification reports"""
    REPORTS_DIR.mkdir(exist_ok=True)

    # JSON report
    json_report = REPORTS_DIR / "ffr_verification_report.json"
    with open(json_report, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nJSON report saved: {json_report}")

    # Text report
    txt_report = REPORTS_DIR / "ffr_verification_report.txt"
    with open(txt_report, 'w', encoding='utf-8') as f:
        f.write("FFR Data Verification Report - COST Action CA19130\n")
        f.write("=" * 60 + "\n")
        f.write(f"Generated: {results['timestamp']}\n\n")

        f.write("COMPARISONS\n")
        f.write("-" * 40 + "\n")
        for comp in results.get("comparisons", []):
            f.write(f"{comp['metric']}: FFR={comp['ffr_value']}, JSON={comp['json_value']} [{comp['status']}]\n")

        f.write("\nFFR DATA BY GRANT PERIOD\n")
        f.write("-" * 40 + "\n")
        for gp in range(1, 6):
            gp_data = results["ffr_data"].get(f"GP{gp}", {})
            f.write(f"\nGP{gp}:\n")
            f.write(f"  Budget: {gp_data.get('budget', 0):,.2f} EUR\n")
            f.write(f"  Actual: {gp_data.get('actual', 0):,.2f} EUR\n")
            f.write(f"  Meetings: {gp_data.get('meetings_count', 0)}\n")
            f.write(f"  Training Schools: {gp_data.get('training_schools_count', 0)}\n")
            f.write(f"  STSMs: {gp_data.get('stsm_count', 0)}\n")
            f.write(f"  VM Grants: {gp_data.get('vm_count', 0)}\n")

        f.write("\nSUMMARY\n")
        f.write("-" * 40 + "\n")
        f.write(f"Total Checks: {results['summary']['total_checks']}\n")
        f.write(f"Passed: {results['summary']['passed']}\n")
        f.write(f"Failed: {results['summary']['failed']}\n")
        f.write(f"Warnings: {results['summary']['warnings']}\n")

    print(f"Text report saved: {txt_report}")


if __name__ == "__main__":
    results = verify_data()
    save_reports(results)
    print("\n" + "=" * 60)
    print("Verification complete!")
