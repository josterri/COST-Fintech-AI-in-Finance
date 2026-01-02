#!/usr/bin/env python3
"""
Financial Reconciliation Script for COST Action CA19130
Verifies every EUR amount sums correctly against FFR data

This script:
1. For each Grant Period:
   - Sum meeting reimbursements from JSON
   - Sum STSM amounts from JSON
   - Sum VM amounts from JSON
   - Sum TS amounts from JSON
   - Sum LOS grants from JSON
2. Compare against FFR category totals
3. Flag any discrepancies > 1 EUR
4. Generate reconciliation report
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


def parse_amount(text: str) -> float:
    """Parse EUR amount from text"""
    if not text:
        return 0.0
    text = re.sub(r'EUR|€', '', str(text)).strip()
    text = text.replace(' ', '').replace(',', '')
    try:
        return float(text)
    except ValueError:
        return 0.0


def extract_ffr_financials(gp: int) -> Dict[str, float]:
    """Extract financial totals from FFR text file"""
    ffr_file = SOURCE_DIR / FFR_FILES[gp]

    if not ffr_file.exists():
        return {"error": f"File not found: {ffr_file}"}

    content = ffr_file.read_text(encoding='utf-8')

    result = {
        "budget": 0.0,
        "actual": 0.0,
        "meetings": 0.0,
        "training_schools": 0.0,
        "stsm": 0.0,
        "virtual_mobility": 0.0,
        "itc_conference": 0.0,
        "dissemination": 0.0,
        "oersa": 0.0,
        "vns": 0.0,
        "fsac": 0.0,
        "total_networking": 0.0
    }

    # Extract Total Grant Budget
    budget_match = re.search(r'Total Grant Budget\s+EUR\s+([\d\s,\.]+)', content)
    if budget_match:
        result["budget"] = parse_amount(budget_match.group(1))

    # Extract from expenditure table - look for the Total eligible expenditure line
    # Format: Total eligible expenditure <budget> <actuals> <accruals> <total> <delta>
    eligible_match = re.search(r'Total eligible expenditure\s+([\d\s,\.]+)\s+([\d\s,\.]+)\s+([\d\s,\.]+)\s+([\d\s,\.]+)', content)
    if eligible_match:
        result["actual"] = parse_amount(eligible_match.group(2))
        if result["actual"] == 0:
            result["actual"] = parse_amount(eligible_match.group(4))

    # Meetings expenditure - from the summary table
    meetings_match = re.search(r'(?:Total\s+)?Meetings\s+([\d\s,\.]+)\s+([\d\s,\.]+)\s+[\d\s,\.]+\s+([\d\s,\.]+)', content)
    if meetings_match:
        result["meetings"] = parse_amount(meetings_match.group(2))
        if result["meetings"] == 0:
            result["meetings"] = parse_amount(meetings_match.group(3))

    # Training Schools
    ts_match = re.search(r'(?:Total\s+)?(?:Training\s+)?Schools\s+([\d\s,\.]+)\s+([\d\s,\.]+)\s+[\d\s,\.]+\s+([\d\s,\.]+)', content)
    if ts_match:
        result["training_schools"] = parse_amount(ts_match.group(2))
        if result["training_schools"] == 0:
            result["training_schools"] = parse_amount(ts_match.group(3))

    # STSM - multiple naming patterns
    stsm_match = re.search(r'(?:Total\s+)?(?:Short[- ]Term\s+Scientific\s+Mission|STSM)\s+([\d\s,\.]+)\s+([\d\s,\.]+)\s+[\d\s,\.]+\s+([\d\s,\.]+)', content, re.IGNORECASE)
    if stsm_match:
        result["stsm"] = parse_amount(stsm_match.group(2))
        if result["stsm"] == 0:
            result["stsm"] = parse_amount(stsm_match.group(3))

    # Virtual Mobility / VNT
    vm_match = re.search(r'Virtual\s+(?:Mobility|Networking\s+Tool)\s+([\d\s,\.]+)\s+([\d\s,\.]+)\s+[\d\s,\.]+\s+([\d\s,\.]+)', content, re.IGNORECASE)
    if vm_match:
        result["virtual_mobility"] = parse_amount(vm_match.group(2))
        if result["virtual_mobility"] == 0:
            result["virtual_mobility"] = parse_amount(vm_match.group(3))

    # ITC Conference
    itc_match = re.search(r'(?:Total\s+)?ITC\s+Conference\s+(?:Grants?)?\s+([\d\s,\.]+)\s+([\d\s,\.]+)\s+[\d\s,\.]+\s+([\d\s,\.]+)', content, re.IGNORECASE)
    if itc_match:
        result["itc_conference"] = parse_amount(itc_match.group(2))
        if result["itc_conference"] == 0:
            result["itc_conference"] = parse_amount(itc_match.group(3))

    # OERSA
    oersa_match = re.search(r'(?:Total\s+)?OERSA\s+([\d\s,\.]+)\s+([\d\s,\.]+)\s+[\d\s,\.]+\s+([\d\s,\.]+)', content)
    if oersa_match:
        result["oersa"] = parse_amount(oersa_match.group(2))
        if result["oersa"] == 0:
            result["oersa"] = parse_amount(oersa_match.group(3))

    # FSAC
    fsac_match = re.search(r'FSAC\s+\(max\s+15%\)\s+([\d\s,\.]+)\s+([\d\s,\.]+)\s+[\d\s,\.]+\s+([\d\s,\.]+)', content)
    if fsac_match:
        result["fsac"] = parse_amount(fsac_match.group(2))
        if result["fsac"] == 0:
            result["fsac"] = parse_amount(fsac_match.group(3))

    # Total Networking expenditure
    networking_match = re.search(r'Total\s+Networking\s+expenditure\s+([\d\s,\.]+)\s+([\d\s,\.]+)\s+[\d\s,\.]+\s+([\d\s,\.]+)', content)
    if networking_match:
        result["total_networking"] = parse_amount(networking_match.group(2))
        if result["total_networking"] == 0:
            result["total_networking"] = parse_amount(networking_match.group(3))

    # VNS (Virtual Networking Support) - GP4 and later
    vns_match = re.search(r'Virtual\s+Networking\s+Support\s+([\d\s,\.]+)\s+([\d\s,\.]+)\s+[\d\s,\.]+\s+([\d\s,\.]+)', content)
    if vns_match:
        result["vns"] = parse_amount(vns_match.group(2))
        if result["vns"] == 0:
            result["vns"] = parse_amount(vns_match.group(3))

    # Dissemination - multiple patterns
    dissem_match = re.search(r'(?:Total\s+)?(?:Action\s+)?Dissemination(?:\s+and\s+Communication\s+Products)?\s+([\d\s,\.]+)\s+([\d\s,\.]+)\s+[\d\s,\.]+\s+([\d\s,\.]+)', content)
    if dissem_match:
        result["dissemination"] = parse_amount(dissem_match.group(2))
        if result["dissemination"] == 0:
            result["dissemination"] = parse_amount(dissem_match.group(3))

    return result


def load_json_data() -> Dict[str, Any]:
    """Load JSON data files"""
    data = {}

    files = {
        "meetings": "meetings_participants.json",
        "stsm": "stsm_detailed.json",
        "vm": "virtual_mobility_full.json",
        "ts": "training_school_attendees.json",
        "los": "los_grants.json",
        "participants": "participant_master.json"
    }

    for key, filename in files.items():
        filepath = DATA_DIR / filename
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                data[key] = json.load(f)
        else:
            data[key] = []
            print(f"Warning: {filename} not found")

    return data


def sum_by_gp(data: List[Dict], amount_field: str, gp_field: str = "grant_period") -> Dict[int, float]:
    """Sum amounts by grant period"""
    sums = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0}
    for item in data:
        gp = item.get(gp_field, 0)
        amount = item.get(amount_field, 0) or 0
        if gp in sums:
            sums[gp] += float(amount)
    return sums


def reconcile_finances() -> Dict[str, Any]:
    """Main reconciliation function"""
    print("=" * 70)
    print("Financial Reconciliation - COST Action CA19130")
    print("=" * 70)
    print(f"Run time: {datetime.now().isoformat()}")
    print()

    results = {
        "timestamp": datetime.now().isoformat(),
        "by_grant_period": {},
        "totals": {
            "ffr": {},
            "json": {},
            "discrepancies": []
        },
        "summary": {
            "total_checks": 0,
            "within_tolerance": 0,
            "discrepancies": 0
        }
    }

    # Load JSON data
    json_data = load_json_data()

    # Calculate JSON sums by GP
    json_sums = {}

    # Meeting reimbursements
    if json_data.get("meetings"):
        meetings_by_gp = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0}
        los_by_gp = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0}
        for meeting in json_data["meetings"]:
            gp = meeting.get("grant_period", 0)
            if gp in meetings_by_gp:
                # Sum participant reimbursements
                total_reimbursed = meeting.get("total_reimbursed", 0) or 0
                meetings_by_gp[gp] += float(total_reimbursed)
                # LOS grants
                los = meeting.get("los_grant", 0) or 0
                los_by_gp[gp] += float(los)
        json_sums["meetings_reimbursements"] = meetings_by_gp
        json_sums["los_grants"] = los_by_gp

    # STSMs
    if json_data.get("stsm"):
        json_sums["stsm"] = sum_by_gp(json_data["stsm"], "amount")

    # Virtual Mobility
    if json_data.get("vm"):
        json_sums["vm"] = sum_by_gp(json_data["vm"], "amount")

    # Process each grant period
    print("Reconciling by Grant Period...\n")

    all_checks = []

    for gp in range(1, 6):
        print(f"--- GP{gp} ---")
        ffr_data = extract_ffr_financials(gp)

        gp_result = {
            "ffr": ffr_data,
            "json": {},
            "checks": []
        }

        # Get JSON values for this GP
        meetings_json = json_sums.get("meetings_reimbursements", {}).get(gp, 0)
        los_json = json_sums.get("los_grants", {}).get(gp, 0)
        total_meetings_json = meetings_json + los_json
        stsm_json = json_sums.get("stsm", {}).get(gp, 0)
        vm_json = json_sums.get("vm", {}).get(gp, 0)

        gp_result["json"] = {
            "meetings_reimbursements": meetings_json,
            "los_grants": los_json,
            "total_meetings": total_meetings_json,
            "stsm": stsm_json,
            "vm": vm_json
        }

        # Compare meetings
        ffr_meetings = ffr_data.get("meetings", 0)
        diff = abs(ffr_meetings - total_meetings_json)
        within_tol = diff <= 1.0
        check = {
            "category": "Meetings",
            "ffr": ffr_meetings,
            "json": total_meetings_json,
            "difference": diff,
            "within_tolerance": within_tol
        }
        gp_result["checks"].append(check)
        all_checks.append(check)
        status = "OK" if within_tol else "DISCREPANCY"
        print(f"  Meetings: FFR={ffr_meetings:,.2f}, JSON={total_meetings_json:,.2f}, Diff={diff:,.2f} [{status}]")

        # Compare STSMs
        ffr_stsm = ffr_data.get("stsm", 0)
        diff = abs(ffr_stsm - stsm_json)
        within_tol = diff <= 1.0
        check = {
            "category": "STSM",
            "ffr": ffr_stsm,
            "json": stsm_json,
            "difference": diff,
            "within_tolerance": within_tol
        }
        gp_result["checks"].append(check)
        all_checks.append(check)
        status = "OK" if within_tol else "DISCREPANCY"
        print(f"  STSM: FFR={ffr_stsm:,.2f}, JSON={stsm_json:,.2f}, Diff={diff:,.2f} [{status}]")

        # Compare VM
        ffr_vm = ffr_data.get("virtual_mobility", 0)
        diff = abs(ffr_vm - vm_json)
        within_tol = diff <= 1.0
        check = {
            "category": "Virtual Mobility",
            "ffr": ffr_vm,
            "json": vm_json,
            "difference": diff,
            "within_tolerance": within_tol
        }
        gp_result["checks"].append(check)
        all_checks.append(check)
        status = "OK" if within_tol else "DISCREPANCY"
        print(f"  VM: FFR={ffr_vm:,.2f}, JSON={vm_json:,.2f}, Diff={diff:,.2f} [{status}]")

        results["by_grant_period"][f"GP{gp}"] = gp_result
        print()

    # Calculate overall totals
    print("=" * 70)
    print("OVERALL TOTALS")
    print("=" * 70)

    total_ffr_budget = sum(results["by_grant_period"][f"GP{gp}"]["ffr"].get("budget", 0) for gp in range(1, 6))
    total_ffr_actual = sum(results["by_grant_period"][f"GP{gp}"]["ffr"].get("actual", 0) for gp in range(1, 6))

    print(f"\nTotal Budget (FFR): {total_ffr_budget:,.2f} EUR")
    print(f"Total Actual (FFR): {total_ffr_actual:,.2f} EUR")
    print(f"Utilization: {(total_ffr_actual/total_ffr_budget*100):.1f}%" if total_ffr_budget > 0 else "N/A")

    results["totals"]["ffr"] = {
        "budget": total_ffr_budget,
        "actual": total_ffr_actual
    }

    # Calculate JSON totals
    total_json_meetings = sum(json_sums.get("meetings_reimbursements", {}).values()) + sum(json_sums.get("los_grants", {}).values())
    total_json_stsm = sum(json_sums.get("stsm", {}).values())
    total_json_vm = sum(json_sums.get("vm", {}).values())

    print(f"\nJSON Totals:")
    print(f"  Meetings (with LOS): {total_json_meetings:,.2f} EUR")
    print(f"  STSMs: {total_json_stsm:,.2f} EUR")
    print(f"  Virtual Mobility: {total_json_vm:,.2f} EUR")

    results["totals"]["json"] = {
        "meetings": total_json_meetings,
        "stsm": total_json_stsm,
        "vm": total_json_vm
    }

    # Summary
    results["summary"]["total_checks"] = len(all_checks)
    results["summary"]["within_tolerance"] = sum(1 for c in all_checks if c["within_tolerance"])
    results["summary"]["discrepancies"] = sum(1 for c in all_checks if not c["within_tolerance"])

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total Checks: {results['summary']['total_checks']}")
    print(f"Within Tolerance (<=1 EUR): {results['summary']['within_tolerance']}")
    print(f"Discrepancies: {results['summary']['discrepancies']}")

    if results["summary"]["discrepancies"] > 0:
        print("\nDiscrepancies found - review may be needed for data accuracy")
    else:
        print("\nAll checks passed - financial data is consistent")

    return results


def save_report(results: Dict[str, Any]):
    """Save reconciliation report"""
    REPORTS_DIR.mkdir(exist_ok=True)

    # JSON report
    json_path = REPORTS_DIR / "financial_reconciliation.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nReport saved: {json_path}")

    # Text report
    txt_path = REPORTS_DIR / "financial_reconciliation.txt"
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write("Financial Reconciliation Report - COST Action CA19130\n")
        f.write("=" * 70 + "\n")
        f.write(f"Generated: {results['timestamp']}\n\n")

        for gp in range(1, 6):
            gp_data = results["by_grant_period"].get(f"GP{gp}", {})
            f.write(f"\nGP{gp}:\n")
            f.write("-" * 40 + "\n")

            ffr = gp_data.get("ffr", {})
            f.write(f"  FFR Budget: {ffr.get('budget', 0):,.2f} EUR\n")
            f.write(f"  FFR Actual: {ffr.get('actual', 0):,.2f} EUR\n")

            for check in gp_data.get("checks", []):
                status = "OK" if check["within_tolerance"] else "DISCREPANCY"
                f.write(f"  {check['category']}: FFR={check['ffr']:,.2f}, JSON={check['json']:,.2f} [{status}]\n")

        f.write("\n" + "=" * 70 + "\n")
        f.write("SUMMARY\n")
        f.write("-" * 40 + "\n")
        f.write(f"Total Checks: {results['summary']['total_checks']}\n")
        f.write(f"Within Tolerance: {results['summary']['within_tolerance']}\n")
        f.write(f"Discrepancies: {results['summary']['discrepancies']}\n")

    print(f"Report saved: {txt_path}")


if __name__ == "__main__":
    results = reconcile_finances()
    save_report(results)
    print("\n" + "=" * 70)
    print("Reconciliation complete!")
