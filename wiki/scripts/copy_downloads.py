"""
COST Action CA19130 Wiki - Copy PDF Reports to Downloads Folder

Organizes official PDFs into wiki/docs/downloads/ structure.
"""

import shutil
from pathlib import Path

# Paths
REPO_ROOT = Path(__file__).parent.parent.parent
DOWNLOADS_DIR = Path(__file__).parent.parent / "docs" / "downloads"

# Key reports to copy
REPORTS_TO_COPY = {
    # Grant Period Annual Reports
    "reports": [
        ("Action Chair/COST GPs Annual Reports/ANNEX-A-R1_AGA-CA19130-1.pdf", "GP1_Annual_Report.pdf"),
        ("Action Chair/COST GPs Annual Reports/ANNEX-A-R1_AGA-CA19130-2.pdf", "GP2_Annual_Report.pdf"),
        ("Action Chair/COST GPs Annual Reports/ANNEX-A-AGA-CA19130-3.pdf", "GP3_Annual_Report.pdf"),
        ("Action Chair/COST GPs Annual Reports/ANNEX-A-R1_AGA-CA19130-4.pdf", "GP4_Annual_Report.pdf"),
        ("Action Chair/COST GPs Annual Reports/ANNEX-A-R1_AGA-CA19130-5.pdf", "GP5_Annual_Report.pdf"),
        ("Action Chair/COST GPs Annual Reports/second_progress_report-CA19130.pdf", "Midterm_Progress_Report.pdf"),
        ("Action Chair/COST GPs Annual Reports/Report Nov 2021 to Mai 2022 COST Action CA19130finalfinalfinalfinal.pdf", "GP2_Narrative_Report.pdf"),
        ("Action Chair/COST GPs Annual Reports/CA19130-e.pdf", "CA19130_Certificate.pdf"),
    ],
    # Work-Based Plans
    "workplans": [
        ("Action Chair/COST GPs Annual Reports/WBP-AGA-CA19130-1_13682.pdf", "GP1_Work_Based_Plan.pdf"),
        ("Action Chair/COST GPs Annual Reports/WBP-AGA-CA19130-2_14713.pdf", "GP2_Work_Based_Plan.pdf"),
        ("Action Chair/COST GPs Annual Reports/WBP-AGA-CA19130-3_14714.pdf", "GP3_Work_Based_Plan.pdf"),
        ("Action Chair/COST GPs Annual Reports/WBP-AGA-CA19130-4_15816.pdf", "GP4_Work_Based_Plan.pdf"),
        ("Action Chair/COST GPs Annual Reports/WBP-AGA-CA19130-5_16959 (1).pdf", "GP5_Work_Based_Plan.pdf"),
    ],
    # Infographics
    "infographics": [
        ("Action Chair/COST GPs Annual Reports/FinalInfograficG2-Nov 2021 to May2022.pdf", "GP2_Infographic.pdf"),
        ("Action Chair/COST GPs Annual Reports/InfograficNovember 2022 to October 2023​.pdf", "GP4_Infographic.pdf"),
    ],
    # COST Framework Documents
    "cost-framework": [
        ("Action Chair/COST_Innovators_Grant/COST Documents/COST-088-21-Level-A-Rules-and-Principles-for-COST-Activities.pdf", "COST_Level_A_Rules.pdf"),
        ("Action Chair/COST_Innovators_Grant/COST Documents/COST-094-21-Annotated-Rules-for-COST-Actions-Level-C-V1.4-Final-.pdf", "COST_Level_C_Annotated_Rules.pdf"),
    ],
    # CIG (COST Innovators Grant)
    "innovators-grant": [
        ("Action Chair/COST_Innovators_Grant/1st_Round_Online_Application/COST CIG CA19130 Application 2024.01.24.pdf", "CIG_Application_2024.pdf"),
        ("Action Chair/COST_Innovators_Grant/2nd_Round_Hearings/IG19130 Evaluation report.pdf", "CIG_Evaluation_Report.pdf"),
    ],
}


def copy_reports():
    """Copy PDF reports to downloads folder."""
    total_copied = 0
    total_failed = 0

    for category, files in REPORTS_TO_COPY.items():
        # Create category folder
        category_dir = DOWNLOADS_DIR / category
        category_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n{category.upper()}:")

        for src_rel, dest_name in files:
            src_path = REPO_ROOT / src_rel
            dest_path = category_dir / dest_name

            if src_path.exists():
                try:
                    shutil.copy2(src_path, dest_path)
                    print(f"  [OK] {dest_name}")
                    total_copied += 1
                except Exception as e:
                    print(f"  [FAIL] {dest_name}: {e}")
                    total_failed += 1
            else:
                print(f"  [MISSING] {src_rel}")
                total_failed += 1

    return total_copied, total_failed


def generate_downloads_index():
    """Generate the downloads index page."""
    md = []
    md.append("# Downloads")
    md.append("")
    md.append("Official documents and reports from COST Action CA19130.")
    md.append("")

    # Reports section
    md.append("## Annual Reports")
    md.append("")
    md.append("| Grant Period | Report | Work-Based Plan |")
    md.append("|--------------|--------|-----------------|")

    for gp in range(1, 6):
        report_file = f"reports/GP{gp}_Annual_Report.pdf"
        wbp_file = f"workplans/GP{gp}_Work_Based_Plan.pdf"

        report_exists = (DOWNLOADS_DIR / report_file).exists()
        wbp_exists = (DOWNLOADS_DIR / wbp_file).exists()

        report_link = f"[Download]({report_file})" if report_exists else "Not available"
        wbp_link = f"[Download]({wbp_file})" if wbp_exists else "Not available"

        md.append(f"| GP{gp} | {report_link} | {wbp_link} |")

    md.append("")

    # Midterm/Final
    md.append("## Progress Reports")
    md.append("")

    midterm = DOWNLOADS_DIR / "reports" / "Midterm_Progress_Report.pdf"
    cert = DOWNLOADS_DIR / "reports" / "CA19130_Certificate.pdf"

    if midterm.exists():
        md.append("- [Midterm Progress Report](reports/Midterm_Progress_Report.pdf)")
    if cert.exists():
        md.append("- [Action Certificate](reports/CA19130_Certificate.pdf)")
    md.append("")

    # Infographics
    md.append("## Infographics")
    md.append("")
    infographics_dir = DOWNLOADS_DIR / "infographics"
    if infographics_dir.exists():
        for pdf in sorted(infographics_dir.glob("*.pdf")):
            md.append(f"- [{pdf.stem.replace('_', ' ')}](infographics/{pdf.name})")
    md.append("")

    # COST Framework
    md.append("## COST Framework Documents")
    md.append("")
    md.append("Official COST documentation governing Action operations.")
    md.append("")

    framework_dir = DOWNLOADS_DIR / "cost-framework"
    if framework_dir.exists():
        for pdf in sorted(framework_dir.glob("*.pdf")):
            title = pdf.stem.replace('_', ' ')
            md.append(f"- [{title}](cost-framework/{pdf.name})")
    md.append("")

    # Innovators Grant
    md.append("## COST Innovators Grant (CIG)")
    md.append("")
    md.append("Documents related to the VisionXAI COST Innovators Grant application.")
    md.append("")

    cig_dir = DOWNLOADS_DIR / "innovators-grant"
    if cig_dir.exists():
        for pdf in sorted(cig_dir.glob("*.pdf")):
            title = pdf.stem.replace('_', ' ')
            md.append(f"- [{title}](innovators-grant/{pdf.name})")
    md.append("")

    # Write index
    index_path = DOWNLOADS_DIR / "index.md"
    index_path.write_text('\n'.join(md), encoding='utf-8')
    print(f"\nGenerated downloads index at {index_path}")


def main():
    """Main entry point."""
    print("=" * 50)
    print("COST Action CA19130 - Copy Downloads")
    print("=" * 50)

    # Create base downloads directory
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

    # Copy reports
    copied, failed = copy_reports()

    print(f"\n{'=' * 50}")
    print(f"Copied: {copied} files")
    print(f"Failed/Missing: {failed} files")

    # Generate index
    generate_downloads_index()

    print("\nDone!")


if __name__ == "__main__":
    main()
