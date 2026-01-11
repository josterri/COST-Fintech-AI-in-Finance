"""Capture screenshots of all COST website pages"""
from playwright.sync_api import sync_playwright
from pathlib import Path
import time

OUTPUT_DIR = Path(__file__).parent / "all_pages"
OUTPUT_DIR.mkdir(exist_ok=True)

BASE_URL = "https://digital-ai-finance.github.io/COST-Fintech-AI-in-Finance"

PAGES = [
    # Root pages
    ("index.html", "homepage"),
    ("impact.html", "impact"),
    ("network.html", "network"),
    ("research.html", "research"),
    ("activities.html", "activities"),
    ("archive.html", "archive"),
    ("members.html", "members"),
    ("mc-members.html", "mc-members"),
    ("wg-members.html", "wg-members"),
    ("leadership.html", "leadership"),
    ("publications.html", "publications"),
    ("final-publications.html", "final-publications"),
    ("preprints.html", "preprints"),
    ("other-outputs.html", "other-outputs"),
    ("final-achievements.html", "final-achievements"),
    ("final-impacts.html", "final-impacts"),
    ("final-report.html", "final-report"),
    ("final-action-chair-report.html", "final-action-chair-report"),
    ("midterm-report.html", "midterm-report"),
    ("midterm-action-chair-report.html", "midterm-action-chair-report"),
    ("midterm-public-report.html", "midterm-public-report"),
    ("progress-reports.html", "progress-reports"),
    ("progress-gp1.html", "progress-gp1"),
    ("progress-gp2.html", "progress-gp2"),
    ("progress-gp3.html", "progress-gp3"),
    ("progress-gp4.html", "progress-gp4"),
    ("progress-gp5.html", "progress-gp5"),
    ("comparison-action-chair.html", "comparison-action-chair"),
    ("comparison-enhanced.html", "comparison-enhanced"),
    ("country-contributions.html", "country-contributions"),
    ("author-stats.html", "author-stats"),
    ("documents.html", "documents"),
    ("datasets.html", "datasets"),
    ("sitemap.html", "sitemap"),
    # Financial reports
    ("financial-reports/overview.html", "fin-overview"),
    ("financial-reports/index.html", "fin-index"),
    ("financial-reports/countries.html", "fin-countries"),
    ("financial-reports/ffr1.html", "fin-ffr1"),
    ("financial-reports/ffr2.html", "fin-ffr2"),
    ("financial-reports/ffr3.html", "fin-ffr3"),
    ("financial-reports/ffr4.html", "fin-ffr4"),
    ("financial-reports/ffr5.html", "fin-ffr5"),
    ("financial-reports/meetings.html", "fin-meetings"),
    ("financial-reports/stsm.html", "fin-stsm"),
    ("financial-reports/training-schools.html", "fin-training-schools"),
    ("financial-reports/virtual-mobility.html", "fin-virtual-mobility"),
    ("financial-reports/participants.html", "fin-participants"),
    # Work budget plans
    ("work-budget-plans/overview.html", "wbp-overview"),
    ("work-budget-plans/index.html", "wbp-index"),
    ("work-budget-plans/deliverables.html", "wbp-deliverables"),
    ("work-budget-plans/working-groups.html", "wbp-working-groups"),
    ("work-budget-plans/gp1.html", "wbp-gp1"),
    ("work-budget-plans/gp2.html", "wbp-gp2"),
    ("work-budget-plans/gp3.html", "wbp-gp3"),
    ("work-budget-plans/gp4.html", "wbp-gp4"),
    ("work-budget-plans/gp5.html", "wbp-gp5"),
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1920, "height": 1080})

    for i, (path, name) in enumerate(PAGES, 1):
        url = f"{BASE_URL}/{path}"
        print(f"[{i}/{len(PAGES)}] Capturing {name}...")
        page.goto(url, wait_until='networkidle')
        page.screenshot(path=str(OUTPUT_DIR / f"{name}.png"), full_page=True)
        time.sleep(0.3)  # Brief delay between captures

    browser.close()
    print(f"\nDone! {len(PAGES)} screenshots saved to {OUTPUT_DIR}")
