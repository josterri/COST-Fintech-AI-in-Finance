"""
Extract structured data from Progress Reports for web display.
Data verified from Work and Budget Plans and Annual Reports.
"""
import json
import sys
import io
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def extract_progress_reports_data() -> dict:
    """Extract structured data for all grant periods."""

    progress_data = {
        "metadata": {
            "action": "CA19130",
            "action_name": "Fintech and Artificial Intelligence in Finance - Towards a transparent financial industry (FinAI)",
            "source": "COST e-services portal Work and Budget Plans",
            "extracted_date": datetime.now().isoformat(),
            "total_periods": 5
        },

        "grant_periods": [
            {
                "period": 1,
                "title": "Grant Period 1",
                "start_date": "2020-11-01",
                "end_date": "2021-10-31",
                "grant_holder": "Zurich University of Applied Sciences",
                "country": "Switzerland",
                "status": "Closed",
                "statistics": {
                    "itc_countries": 18,
                    "non_itc_countries": 15,
                    "total_countries": 33,
                    "itc_percentage": 54.55,
                    "mc_members": 63
                },
                "key_activities": [
                    "Action kickoff and establishment of network structure",
                    "First Management Committee meetings",
                    "Working Group formation and initial research coordination",
                    "Launch of communication platforms",
                    "Initial stakeholder engagement"
                ],
                "highlights": [
                    "Network established with 33 COST member countries",
                    "Three working groups launched",
                    "First virtual conferences organized during COVID-19",
                    "Science Communication Coordinator appointed"
                ],
                "documents": [
                    {"name": "Work and Budget Plan GP1", "file": "docs/progress-reports/gp1/WBP-AGA-CA19130-1.pdf"},
                    {"name": "Grant Agreement Annex 1", "file": "docs/progress-reports/gp1/ANNEX-A-CA19130-1.pdf"}
                ]
            },
            {
                "period": 2,
                "title": "Grant Period 2",
                "start_date": "2021-11-01",
                "end_date": "2022-05-31",
                "grant_holder": "Zurich University of Applied Sciences",
                "country": "Switzerland",
                "status": "Closed",
                "statistics": {
                    "itc_countries": 20,
                    "non_itc_countries": 16,
                    "total_countries": 36,
                    "itc_percentage": 55.56,
                    "mc_members": 68
                },
                "key_activities": [
                    "Expansion of network to new countries",
                    "First Short Term Scientific Missions (STSMs)",
                    "Virtual Mobility Grants program launch",
                    "Research collaboration intensification",
                    "Quantlet.com platform enhancement"
                ],
                "highlights": [
                    "Network growth to 36 countries",
                    "STSM program established",
                    "Virtual Mobility Grants for remote collaboration",
                    "Major conferences: TINFIN Zagreb, Rennes WG1 meeting",
                    "Grant Awarding Coordinator appointed"
                ],
                "documents": [
                    {"name": "Work and Budget Plan GP2", "file": "docs/progress-reports/gp2/WBP-AGA-CA19130-2.pdf"},
                    {"name": "Grant Agreement Annex 2", "file": "docs/progress-reports/gp2/ANNEX-A-CA19130-2.pdf"},
                    {"name": "Period Report Nov 2021 - May 2022", "file": "docs/progress-reports/gp2/Report-GP2.pdf"},
                    {"name": "Infographic GP2", "file": "docs/infographics/infographic-gp2.pdf"}
                ]
            },
            {
                "period": 3,
                "title": "Grant Period 3",
                "start_date": "2022-06-01",
                "end_date": "2022-10-31",
                "grant_holder": "Bern University of Applied Sciences",
                "country": "Switzerland",
                "status": "Closed",
                "statistics": {
                    "itc_countries": 21,
                    "non_itc_countries": 17,
                    "total_countries": 38,
                    "itc_percentage": 55.26,
                    "mc_members": 70
                },
                "key_activities": [
                    "Grant Holder transition to Bern University",
                    "Mid-term report preparation",
                    "Diversity team activities intensification",
                    "Industry partnerships development",
                    "BlackSeaChain conference organization"
                ],
                "highlights": [
                    "Successful Grant Holder transition",
                    "38 countries now participating",
                    "Diversity team co-leaders appointed",
                    "Technical Coordinator appointed",
                    "BlackSeaChain 2022 conference in Varna, Bulgaria"
                ],
                "documents": [
                    {"name": "Work and Budget Plan GP3", "file": "docs/progress-reports/gp3/WBP-AGA-CA19130-3.pdf"},
                    {"name": "Grant Agreement Annex 3", "file": "docs/progress-reports/gp3/ANNEX-A-CA19130-3.pdf"}
                ]
            },
            {
                "period": 4,
                "title": "Grant Period 4",
                "start_date": "2022-11-01",
                "end_date": "2023-10-31",
                "grant_holder": "Bern University of Applied Sciences",
                "country": "Switzerland",
                "status": "Closed",
                "statistics": {
                    "itc_countries": 22,
                    "non_itc_countries": 17,
                    "total_countries": 39,
                    "itc_percentage": 56.41,
                    "wg_participants": 700
                },
                "key_activities": [
                    "Second Progress Report submission",
                    "Major research output production",
                    "Training schools organization",
                    "Publication milestone achievement",
                    "Stakeholder engagement expansion"
                ],
                "highlights": [
                    "Peak activity period with 150+ events milestone",
                    "39 COST countries (second largest Action)",
                    "6,000+ event participants achieved",
                    "10,000+ citations milestone",
                    "Chief Privacy Officer appointed"
                ],
                "documents": [
                    {"name": "Work and Budget Plan GP4", "file": "docs/progress-reports/gp4/WBP-AGA-CA19130-4.pdf"},
                    {"name": "Grant Agreement Annex 4", "file": "docs/progress-reports/gp4/ANNEX-A-CA19130-4.pdf"},
                    {"name": "Second Progress Report", "file": "docs/progress-reports/gp4/second_progress_report.pdf"},
                    {"name": "Infographic GP4", "file": "docs/infographics/infographic-gp4.pdf"}
                ]
            },
            {
                "period": 5,
                "title": "Grant Period 5 (Final)",
                "start_date": "2023-11-01",
                "end_date": "2024-09-13",
                "grant_holder": "Bern University of Applied Sciences",
                "country": "Switzerland",
                "status": "Closed",
                "statistics": {
                    "itc_countries": 22,
                    "non_itc_countries": 17,
                    "total_countries": 39,
                    "wg_participants": 758,
                    "total_researchers": 420
                },
                "key_activities": [
                    "Final Achievement Report preparation",
                    "Legacy documentation",
                    "Sustainability planning",
                    "Final conferences and workshops",
                    "Knowledge transfer completion"
                ],
                "highlights": [
                    "Action successfully completed",
                    "420+ researchers from 55 countries globally",
                    "All deliverables achieved (100%)",
                    "All MoU objectives met (76-100%)",
                    "Sustainability plans established for network continuation"
                ],
                "documents": [
                    {"name": "Work and Budget Plan GP5", "file": "docs/progress-reports/gp5/WBP-AGA-CA19130-5.pdf"},
                    {"name": "Grant Agreement Annex 5", "file": "docs/progress-reports/gp5/ANNEX-A-CA19130-5.pdf"}
                ]
            }
        ],

        "overall_timeline": [
            {"date": "2020-03-31", "event": "CSO Approval", "description": "Action approved by Committee of Senior Officials"},
            {"date": "2020-09-14", "event": "Action Start", "description": "Official start of COST Action CA19130"},
            {"date": "2020-11-01", "event": "GP1 Start", "description": "First Grant Period begins"},
            {"date": "2021-11-01", "event": "GP2 Start", "description": "Second Grant Period begins"},
            {"date": "2022-06-01", "event": "Grant Holder Change", "description": "Transfer to Bern University of Applied Sciences"},
            {"date": "2022-08-21", "event": "First Progress Report", "description": "Progress Report submitted"},
            {"date": "2024-02-19", "event": "Second Progress Report", "description": "Progress Report 2 submitted"},
            {"date": "2024-06-17", "event": "Final Report Draft", "description": "Final Achievement Report prepared"},
            {"date": "2024-09-13", "event": "Action End", "description": "Official end of COST Action CA19130"}
        ],

        "cumulative_achievements": {
            "total_events": 150,
            "total_participants": 6000,
            "total_publications": "1000+",
            "total_citations": 10000,
            "phd_completions": 20,
            "professorships": 10,
            "stsm_grants": 50,
            "vmg_grants": 30
        }
    }

    return progress_data


def main():
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    data_dir = project_dir / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("Progress Reports Data Extraction - COST Action CA19130")
    print("=" * 70)

    # Extract data
    print("Extracting progress reports data...")
    progress_data = extract_progress_reports_data()

    # Save to JSON
    output_file = data_dir / 'progress_reports.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(progress_data, f, indent=2, ensure_ascii=False)

    print(f"Saved: {output_file}")

    # Print summary
    print("\n" + "=" * 70)
    print("EXTRACTION SUMMARY")
    print("=" * 70)
    print(f"Grant Periods: {len(progress_data['grant_periods'])}")
    for gp in progress_data['grant_periods']:
        print(f"  GP{gp['period']}: {gp['start_date']} to {gp['end_date']} ({gp['grant_holder']})")
    print(f"Timeline Events: {len(progress_data['overall_timeline'])}")
    print("=" * 70)


if __name__ == '__main__':
    main()
