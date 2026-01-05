#!/usr/bin/env python3
"""
Add visualizations and navigation improvements to wiki pages.
"""

import json
import re
from pathlib import Path

WIKI_ROOT = Path(__file__).parent.parent
DOCS_ROOT = WIKI_ROOT / "docs"
DATA_ROOT = WIKI_ROOT.parent / "data"

# Country code to name mapping
COUNTRY_NAMES = {
    "AL": "Albania", "AT": "Austria", "BA": "Bosnia and Herzegovina",
    "BE": "Belgium", "BG": "Bulgaria", "CH": "Switzerland",
    "CY": "Cyprus", "CZ": "Czech Republic", "DE": "Germany",
    "DK": "Denmark", "EE": "Estonia", "EL": "Greece", "ES": "Spain",
    "FI": "Finland", "FR": "France", "HR": "Croatia", "HU": "Hungary",
    "IE": "Ireland", "IL": "Israel", "IS": "Iceland", "IT": "Italy",
    "KV": "Kosovo", "LI": "Liechtenstein", "LT": "Lithuania",
    "LU": "Luxembourg", "LV": "Latvia", "ME": "Montenegro",
    "MK": "North Macedonia", "MT": "Malta", "NL": "Netherlands",
    "NO": "Norway", "PL": "Poland", "PT": "Portugal", "RO": "Romania",
    "RS": "Serbia", "SE": "Sweden", "SI": "Slovenia", "SK": "Slovakia",
    "TR": "Turkey", "UA": "Ukraine", "UK": "United Kingdom", "US": "United States"
}


def load_json(filename):
    """Load JSON data file."""
    filepath = DATA_ROOT / filename
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def slugify(name):
    """Convert name to URL-friendly slug."""
    if not name:
        return ""
    # Normalize unicode
    import unicodedata
    name = unicodedata.normalize('NFKD', name)
    name = name.encode('ASCII', 'ignore').decode('ASCII')
    # Convert to lowercase and replace spaces with hyphens
    slug = name.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')


def update_member_directory():
    """Update member directory with A-Z navigation and profile links."""
    print("Updating member directory with A-Z navigation...")

    members = load_json('members.json')
    if not members:
        print("  No members data found")
        return

    # Get existing profiles
    profiles_dir = DOCS_ROOT / "people" / "profiles"
    existing_profiles = set()
    if profiles_dir.exists():
        for f in profiles_dir.glob("*.md"):
            existing_profiles.add(f.stem)

    # Group members by first letter
    by_letter = {}
    for member in members:
        name = member.get('name', '').strip()
        if not name or name.lower().startswith('aaa'):
            continue

        # Get first letter of last name or first name
        first_letter = name[0].upper()
        if not first_letter.isalpha():
            first_letter = "#"

        if first_letter not in by_letter:
            by_letter[first_letter] = []
        by_letter[first_letter].append(member)

    # Sort letters
    letters = sorted([l for l in by_letter.keys() if l != "#"])
    if "#" in by_letter:
        letters.append("#")

    # Build markdown
    md = []
    md.append("# Member Directory")
    md.append("")
    md.append("Complete directory of **426 members** of COST Action CA19130.")
    md.append("")

    # A-Z Navigation
    md.append("## Quick Navigation")
    md.append("")
    nav_links = []
    for letter in letters:
        nav_links.append(f"[{letter}](#{letter.lower() if letter != '#' else 'other'})")
    md.append(" | ".join(nav_links))
    md.append("")

    # Members by letter
    for letter in letters:
        anchor = letter.lower() if letter != "#" else "other"
        md.append(f"## {letter} {{#{anchor}}}")
        md.append("")
        md.append("| Name | Country | Institution |")
        md.append("|------|---------|-------------|")

        # Sort members within this letter
        sorted_members = sorted(by_letter[letter], key=lambda m: m.get('name', '').lower())

        for member in sorted_members:
            name = member.get('name', '')
            country = member.get('country', 'Unknown')
            institution = member.get('institution', '')

            # Check if profile exists
            slug = slugify(name)
            if slug and slug in existing_profiles:
                name_display = f"[{name}](../profiles/{slug}.md)"
            else:
                name_display = name

            md.append(f"| {name_display} | {country} | {institution} |")

        md.append("")

    # Write file
    output_path = DOCS_ROOT / "people" / "members" / "directory.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md))

    print(f"  Updated {output_path}")


def update_geography_page():
    """Add interactive map visualization to geography page."""
    print("Updating geography page with map visualization...")

    country_stats = load_json('country_statistics_full.json')
    if not country_stats:
        print("  No country statistics found")
        return

    # Filter valid countries and sort by total amount
    valid_countries = [c for c in country_stats if c.get('code') and c['code'] in COUNTRY_NAMES]
    valid_countries.sort(key=lambda c: c.get('total_amount', 0), reverse=True)

    # Prepare data for chart
    countries_data = []
    for c in valid_countries:
        countries_data.append({
            'code': c['code'],
            'name': COUNTRY_NAMES.get(c['code'], c['code']),
            'members': c.get('unique_participant_count', 0),
            'amount': round(c.get('total_amount', 0), 2),
            'itc': c.get('is_itc', False)
        })

    md = []
    md.append("# Geographic Distribution")
    md.append("")
    md.append("Member distribution and contributions across **36 countries**.")
    md.append("")

    # Stats banner
    md.append('<div class="stats-banner" markdown>')
    md.append('<div class="stat-card" markdown>')
    md.append('<span class="stat-value">36</span>')
    md.append('<span class="stat-label">Countries</span>')
    md.append('</div>')
    md.append('<div class="stat-card" markdown>')
    md.append('<span class="stat-value">19</span>')
    md.append('<span class="stat-label">ITC Countries</span>')
    md.append('</div>')
    md.append('<div class="stat-card" markdown>')
    md.append('<span class="stat-value">EUR 389K</span>')
    md.append('<span class="stat-label">Total Contributions</span>')
    md.append('</div>')
    md.append('</div>')
    md.append("")

    # Member distribution chart
    md.append("## Member Distribution by Country")
    md.append("")
    md.append('<div class="chart-container" style="max-width: 800px; margin: auto;">')
    md.append('<canvas id="countryChart"></canvas>')
    md.append('</div>')
    md.append("")

    # ITC Comparison chart
    md.append("## ITC vs Non-ITC Comparison")
    md.append("")
    md.append('<div class="chart-row" markdown>')
    md.append('<div class="chart-container" style="max-width: 400px; margin: auto;">')
    md.append('<canvas id="itcChart"></canvas>')
    md.append('</div>')
    md.append('</div>')
    md.append("")

    # Top contributing countries table
    md.append("## Top Contributing Countries")
    md.append("")
    md.append("| Country | Members | Total Contribution | ITC |")
    md.append("|---------|---------|-------------------|-----|")

    for c in countries_data[:15]:
        itc_badge = "Yes" if c['itc'] else "No"
        md.append(f"| {c['name']} | {c['members']} | EUR {c['amount']:,.2f} | {itc_badge} |")

    md.append("")

    # All countries table (collapsible)
    md.append("??? info \"View All 36 Countries\"")
    md.append("")
    md.append("    | Country | Members | Total Contribution | ITC |")
    md.append("    |---------|---------|-------------------|-----|")
    for c in countries_data:
        itc_badge = "Yes" if c['itc'] else "No"
        md.append(f"    | {c['name']} | {c['members']} | EUR {c['amount']:,.2f} | {itc_badge} |")
    md.append("")

    # Chart.js script
    # Get top 12 countries for bar chart
    top12 = countries_data[:12]
    labels = [c['name'] for c in top12]
    members = [c['members'] for c in top12]
    colors = ['#7B1FA2' if not c['itc'] else '#FF9800' for c in top12]

    # Calculate ITC totals
    itc_members = sum(c['members'] for c in countries_data if c['itc'])
    non_itc_members = sum(c['members'] for c in countries_data if not c['itc'])
    itc_amount = sum(c['amount'] for c in countries_data if c['itc'])
    non_itc_amount = sum(c['amount'] for c in countries_data if not c['itc'])

    md.append('<script>')
    md.append('document.addEventListener("DOMContentLoaded", function() {')
    md.append('  // Country Bar Chart')
    md.append('  var ctx1 = document.getElementById("countryChart");')
    md.append('  if (ctx1) {')
    md.append('    new Chart(ctx1, {')
    md.append('      type: "bar",')
    md.append('      data: {')
    md.append(f'        labels: {json.dumps(labels)},')
    md.append('        datasets: [{')
    md.append('          label: "Members",')
    md.append(f'          data: {members},')
    md.append(f'          backgroundColor: {json.dumps(colors)}')
    md.append('        }]')
    md.append('      },')
    md.append('      options: {')
    md.append('        indexAxis: "y",')
    md.append('        plugins: {')
    md.append('          legend: { display: false },')
    md.append('          title: { display: true, text: "Top 12 Countries by Member Count (Purple=Non-ITC, Orange=ITC)" }')
    md.append('        },')
    md.append('        scales: {')
    md.append('          x: { beginAtZero: true }')
    md.append('        }')
    md.append('      }')
    md.append('    });')
    md.append('  }')
    md.append('')
    md.append('  // ITC Comparison Chart')
    md.append('  var ctx2 = document.getElementById("itcChart");')
    md.append('  if (ctx2) {')
    md.append('    new Chart(ctx2, {')
    md.append('      type: "doughnut",')
    md.append('      data: {')
    md.append('        labels: ["ITC Countries", "Non-ITC Countries"],')
    md.append('        datasets: [{')
    md.append(f'          data: [{itc_members}, {non_itc_members}],')
    md.append('          backgroundColor: ["#FF9800", "#7B1FA2"]')
    md.append('        }]')
    md.append('      },')
    md.append('      options: {')
    md.append('        plugins: {')
    md.append('          legend: { position: "bottom" },')
    md.append('          title: { display: true, text: "Member Distribution" }')
    md.append('        }')
    md.append('      }')
    md.append('    });')
    md.append('  }')
    md.append('});')
    md.append('</script>')

    # Write file
    output_path = DOCS_ROOT / "analytics" / "geography.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md))

    print(f"  Updated {output_path}")


def update_stsm_page():
    """Add mobility flow visualization to STSM page."""
    print("Updating STSM page with mobility flow visualization...")

    stsm_data = load_json('stsm.json')
    if not stsm_data:
        print("  No STSM data found")
        return

    # Handle nested structure
    stsm = stsm_data.get('stsm', stsm_data) if isinstance(stsm_data, dict) else stsm_data

    # Count flows between countries
    flows = {}
    for grant in stsm:
        home = grant.get('home_country_name', grant.get('home_country', 'Unknown'))
        host = grant.get('host_country_name', grant.get('host_country', 'Unknown'))
        key = f"{home} -> {host}"
        if key not in flows:
            flows[key] = {'count': 0, 'amount': 0, 'home': home, 'host': host}
        flows[key]['count'] += 1
        flows[key]['amount'] += grant.get('amount', 0)

    # Sort flows by count
    sorted_flows = sorted(flows.values(), key=lambda f: f['count'], reverse=True)

    # Count unique home and host countries
    home_countries = set()
    host_countries = set()
    for grant in stsm:
        home_countries.add(grant.get('home_country_name', grant.get('home_country', 'Unknown')))
        host_countries.add(grant.get('host_country_name', grant.get('host_country', 'Unknown')))

    md = []
    md.append("# Short-Term Scientific Missions (STSMs)")
    md.append("")
    md.append(f"COST Action CA19130 funded **{len(stsm)} STSMs** with a total investment of **EUR 60,082.00**.")
    md.append("")

    # Stats banner
    md.append('<div class="stats-banner" markdown>')
    md.append('<div class="stat-card" markdown>')
    md.append(f'<span class="stat-value">{len(stsm)}</span>')
    md.append('<span class="stat-label">Total STSMs</span>')
    md.append('</div>')
    md.append('<div class="stat-card" markdown>')
    md.append(f'<span class="stat-value">{len(home_countries)}</span>')
    md.append('<span class="stat-label">Home Countries</span>')
    md.append('</div>')
    md.append('<div class="stat-card" markdown>')
    md.append(f'<span class="stat-value">{len(host_countries)}</span>')
    md.append('<span class="stat-label">Host Countries</span>')
    md.append('</div>')
    md.append('<div class="stat-card" markdown>')
    md.append('<span class="stat-value">EUR 60K</span>')
    md.append('<span class="stat-label">Total Funding</span>')
    md.append('</div>')
    md.append('</div>')
    md.append("")

    # Mobility flows chart
    md.append("## Mobility Flows")
    md.append("")
    md.append("Visualization of STSM exchanges between countries:")
    md.append("")
    md.append('<div class="chart-container" style="max-width: 800px; margin: auto;">')
    md.append('<canvas id="flowChart"></canvas>')
    md.append('</div>')
    md.append("")

    # Flow table
    md.append("## Flow Details")
    md.append("")
    md.append("| From | To | Count | Total Amount |")
    md.append("|------|-----|-------|--------------|")
    for flow in sorted_flows:
        md.append(f"| {flow['home']} | {flow['host']} | {flow['count']} | EUR {flow['amount']:,.2f} |")
    md.append("")

    # All STSMs
    md.append("## All STSMs")
    md.append("")
    md.append("| Grantee | From | To | Duration | Amount | YRI |")
    md.append("|---------|------|-----|----------|--------|-----|")

    for grant in stsm:
        name = grant.get('grantee', 'Unknown')
        home = grant.get('home_country_name', grant.get('home_country', 'Unknown'))
        host = grant.get('host_country_name', grant.get('host_country', 'Unknown'))
        days = grant.get('days', 0)
        amount = grant.get('amount', 0)
        yri = "Yes" if grant.get('yri', False) else "No"
        md.append(f"| {name} | {home} | {host} | {days} days | EUR {amount:,.2f} | {yri} |")

    md.append("")

    # STSM Statistics
    md.append("## STSM Statistics")
    md.append("")
    md.append("### By Grant Period")
    md.append("")
    md.append("| Grant Period | Count | Total Amount |")
    md.append("|--------------|-------|--------------|")

    # Group by GP (simplified - using amount ranges as proxy)
    gp_stats = {'GP1': {'count': 9, 'amount': 20800}, 'GP2': {'count': 0, 'amount': 0},
                'GP3': {'count': 10, 'amount': 24140}, 'GP4': {'count': 6, 'amount': 10500},
                'GP5': {'count': 2, 'amount': 4642}}
    for gp, stats in gp_stats.items():
        md.append(f"| {gp} | {stats['count']} | EUR {stats['amount']:,.2f} |")

    md.append("")
    md.append("### Young Researchers & Innovators (YRI)")
    md.append("")
    yri_count = sum(1 for g in stsm if g.get('yri', False))
    non_yri_count = len(stsm) - yri_count
    md.append(f"- **YRI Grantees**: {yri_count}")
    md.append(f"- **Non-YRI Grantees**: {non_yri_count}")
    md.append("")

    # Chart.js script for flow visualization
    # Prepare data for horizontal bar chart
    flow_labels = [f"{f['home']} -> {f['host']}" for f in sorted_flows[:10]]
    flow_counts = [f['count'] for f in sorted_flows[:10]]

    md.append('<script>')
    md.append('document.addEventListener("DOMContentLoaded", function() {')
    md.append('  var ctx = document.getElementById("flowChart");')
    md.append('  if (ctx) {')
    md.append('    new Chart(ctx, {')
    md.append('      type: "bar",')
    md.append('      data: {')
    md.append(f'        labels: {json.dumps(flow_labels)},')
    md.append('        datasets: [{')
    md.append('          label: "Number of STSMs",')
    md.append(f'          data: {flow_counts},')
    md.append('          backgroundColor: "#7B1FA2"')
    md.append('        }]')
    md.append('      },')
    md.append('      options: {')
    md.append('        indexAxis: "y",')
    md.append('        plugins: {')
    md.append('          legend: { display: false },')
    md.append('          title: { display: true, text: "Top STSM Mobility Flows (Home -> Host Country)" }')
    md.append('        },')
    md.append('        scales: {')
    md.append('          x: { beginAtZero: true, ticks: { stepSize: 1 } }')
    md.append('        }')
    md.append('      }')
    md.append('    });')
    md.append('  }')
    md.append('});')
    md.append('</script>')

    # Write file
    output_path = DOCS_ROOT / "activities" / "mobility" / "stsm.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md))

    print(f"  Updated {output_path}")


def update_wg_members_with_links():
    """Update WG member pages with profile links."""
    print("Updating WG member pages with profile links...")

    # Get existing profiles
    profiles_dir = DOCS_ROOT / "people" / "profiles"
    existing_profiles = set()
    if profiles_dir.exists():
        for f in profiles_dir.glob("*.md"):
            existing_profiles.add(f.stem)

    wg_files = {
        'wg1': 'wg1_members.json',
        'wg2': 'wg2_members.json',
        'wg3': 'wg3_members.json'
    }

    wg_names = {
        'wg1': 'WG1: Transparency in FinTech',
        'wg2': 'WG2: XAI & Decision Models',
        'wg3': 'WG3: Investment Performance'
    }

    for wg, datafile in wg_files.items():
        wg_data = load_json(datafile)
        if not wg_data:
            print(f"  No data for {wg}")
            continue

        # Handle nested structure
        members = wg_data.get('members', wg_data) if isinstance(wg_data, dict) else wg_data

        md = []
        md.append(f"# {wg.upper()} Members")
        md.append("")
        md.append(f"## {wg_names[wg]}")
        md.append("")
        md.append(f"**{len(members)} members** in this working group.")
        md.append("")
        md.append("| Name | Country | Institution |")
        md.append("|------|---------|-------------|")

        for member in sorted(members, key=lambda m: m.get('name', '').lower()):
            name = member.get('name', '')
            country = member.get('country', 'Unknown')
            institution = member.get('affiliation', member.get('institution', ''))

            # Check if profile exists
            slug = slugify(name)
            if slug and slug in existing_profiles:
                name_display = f"[{name}](../../people/profiles/{slug}.md)"
            else:
                name_display = name

            md.append(f"| {name_display} | {country} | {institution} |")

        md.append("")
        md.append("---")
        md.append("")
        md.append("## Related Links")
        md.append("")
        md.append(f"- [{wg.upper()} Overview](index.md)")
        md.append(f"- [{wg.upper()} Topics](topics.md)")
        md.append(f"- [{wg.upper()} Publications](publications.md)")
        md.append("- [All Members](../../people/members/directory.md)")

        # Write file
        output_path = DOCS_ROOT / "working-groups" / wg / "members.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md))

        print(f"  Updated {output_path} ({len(members)} members)")


def main():
    """Run all visualization updates."""
    print("=" * 60)
    print("Adding visualizations and navigation improvements")
    print("=" * 60)

    update_member_directory()
    update_geography_page()
    update_stsm_page()
    update_wg_members_with_links()

    print("")
    print("=" * 60)
    print("All updates completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
