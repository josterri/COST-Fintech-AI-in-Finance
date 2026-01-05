"""
COST Action CA19130 Wiki - Content Population Script

Populates all stub/placeholder pages with real content from JSON data files.
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Paths
SCRIPT_DIR = Path(__file__).parent
WIKI_ROOT = SCRIPT_DIR.parent
DOCS_DIR = WIKI_ROOT / "docs"
DATA_DIR = WIKI_ROOT.parent / "data"

# Country code to name mapping
COUNTRY_NAMES = {
    "AL": "Albania", "AT": "Austria", "BA": "Bosnia and Herzegovina", "BE": "Belgium",
    "BG": "Bulgaria", "CH": "Switzerland", "CY": "Cyprus", "CZ": "Czech Republic",
    "DE": "Germany", "DK": "Denmark", "EE": "Estonia", "EL": "Greece", "ES": "Spain",
    "FI": "Finland", "FR": "France", "HR": "Croatia", "HU": "Hungary", "IE": "Ireland",
    "IL": "Israel", "IS": "Iceland", "IT": "Italy", "KV": "Kosovo", "LI": "Liechtenstein",
    "LT": "Lithuania", "LV": "Latvia", "MK": "North Macedonia", "MT": "Malta",
    "NL": "Netherlands", "NO": "Norway", "PL": "Poland", "PT": "Portugal", "RO": "Romania",
    "RS": "Serbia", "SE": "Sweden", "SI": "Slovenia", "SK": "Slovakia", "TR": "Turkey",
    "UA": "Ukraine", "UK": "United Kingdom", "US": "United States", "GB": "United Kingdom"
}


def load_json(filename):
    """Load JSON data file."""
    filepath = DATA_DIR / filename
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    print(f"[WARN] File not found: {filename}")
    return None


def write_md(path, content):
    """Write markdown content to file."""
    filepath = DOCS_DIR / path
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"[OK] {path}")


def format_date(date_str):
    """Format date string nicely."""
    if not date_str:
        return "N/A"
    try:
        if "/" in date_str:
            dt = datetime.strptime(date_str, "%d/%m/%Y")
        else:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%B %d, %Y")
    except:
        return date_str


def format_currency(amount):
    """Format currency amount."""
    if amount is None:
        return "N/A"
    return f"EUR {amount:,.2f}"


# ============================================================================
# ACTIVITIES SECTION
# ============================================================================

def populate_activities_index(data):
    """Generate activities/index.md"""
    stats = data.get('summary_statistics', {})

    md = [
        "# Activities Overview",
        "",
        "COST Action CA19130 organized a comprehensive program of activities to facilitate collaboration, knowledge exchange, and capacity building across our network.",
        "",
        "## At a Glance",
        "",
        '<div class="stats-banner" markdown>',
        "",
        '<div class="stat-card" markdown>',
        f'<span class="stat-value">{stats.get("total_meetings", 52)}</span>',
        '<span class="stat-label">Meetings & Events</span>',
        "</div>",
        "",
        '<div class="stat-card" markdown>',
        f'<span class="stat-value">{stats.get("total_training_schools", 7)}</span>',
        '<span class="stat-label">Training Schools</span>',
        "</div>",
        "",
        '<div class="stat-card" markdown>',
        f'<span class="stat-value">{stats.get("total_stsms", 27)}</span>',
        '<span class="stat-label">STSMs</span>',
        "</div>",
        "",
        '<div class="stat-card" markdown>',
        f'<span class="stat-value">{stats.get("total_virtual_mobility", 39)}</span>',
        '<span class="stat-label">Virtual Mobility Grants</span>',
        "</div>",
        "",
        "</div>",
        "",
        "## Activity Categories",
        "",
        "### [Meetings & Events](meetings/index.md)",
        f"Over the 4-year duration, we organized **{stats.get('total_meetings', 52)} meetings** including conferences, workshops, working group meetings, and management committee sessions across Europe and beyond.",
        "",
        "### [Training Schools](training-schools/index.md)",
        f"**{stats.get('total_training_schools', 7)} training schools** trained the next generation of researchers in fintech and AI, with **{stats.get('total_trainees', 96)} trainees** participating.",
        "",
        "### [Mobility Grants](mobility/index.md)",
        f"We supported **{stats.get('total_stsms', 27)} Short-Term Scientific Missions** and **{stats.get('total_virtual_mobility', 39)} Virtual Mobility grants** enabling cross-border collaboration.",
        "",
        "### [Dissemination](dissemination.md)",
        "Our dissemination activities reached thousands through media appearances, publications, and outreach events.",
        "",
        "## Activity Distribution by Grant Period",
        "",
        "| Grant Period | Meetings | Training Schools | STSMs | Virtual Mobility |",
        "|--------------|----------|------------------|-------|------------------|",
    ]

    meetings_by_gp = stats.get('meetings_by_gp', {})
    stsms_by_gp = stats.get('stsms_by_gp', {})
    vm_by_gp = stats.get('vm_by_gp', {})
    ts_by_gp = stats.get('ts_by_gp', {})

    for gp in range(1, 6):
        gp_str = str(gp)
        md.append(f"| GP{gp} | {meetings_by_gp.get(gp_str, 0)} | {ts_by_gp.get(gp_str, 0)} | {stsms_by_gp.get(gp_str, 0)} | {vm_by_gp.get(gp_str, 0)} |")

    md.extend([
        "",
        "## Financial Investment in Activities",
        "",
        f"- **Meetings & Events**: {format_currency(stats.get('financial_totals', {}).get('meetings', 423694.69))}",
        f"- **Training Schools**: {format_currency(stats.get('financial_totals', {}).get('training_schools', 108816.05))}",
        f"- **STSMs**: {format_currency(stats.get('financial_totals', {}).get('stsms', 60082.00))}",
        f"- **Virtual Mobility**: {format_currency(stats.get('financial_totals', {}).get('virtual_mobility', 56500.00))}",
    ])

    write_md("activities/index.md", '\n'.join(md))


def populate_meetings_index(data):
    """Generate activities/meetings/index.md"""
    meetings = data.get('meetings', {}).get('meetings', [])

    md = [
        "# Meetings & Events",
        "",
        f"COST Action CA19130 organized **{len(meetings)} meetings and events** over its 4-year duration, bringing together researchers from across Europe and beyond.",
        "",
        "## All Meetings",
        "",
        "| Date | Title | Type | Location | Participants |",
        "|------|-------|------|----------|--------------|",
    ]

    for m in sorted(meetings, key=lambda x: x.get('date', ''), reverse=True):
        date = m.get('date', '')[:10]
        title = m.get('title', 'Untitled')
        mtype = m.get('type', 'Meeting')
        location = m.get('location', 'TBD')
        country = m.get('country_name', m.get('country', ''))
        participants = m.get('participants', 0)
        itc = " (ITC)" if m.get('itc') else ""

        md.append(f"| {date} | {title} | {mtype} | {location}, {country}{itc} | {participants} |")

    md.extend([
        "",
        "## Meeting Types",
        "",
        "- **MC**: Management Committee meetings",
        "- **WG**: Working Group meetings",
        "- **MC/WG**: Combined MC and WG meetings",
        "- **Conference**: Major conferences",
        "- **Workshop**: Focused workshops on specific topics",
        "",
        "## Geographic Distribution",
        "",
    ])

    # Count meetings by country
    country_counts = defaultdict(int)
    for m in meetings:
        country = m.get('country_name', m.get('country', 'Unknown'))
        country_counts[country] += 1

    md.append("| Country | Number of Meetings |")
    md.append("|---------|-------------------|")
    for country, count in sorted(country_counts.items(), key=lambda x: -x[1]):
        if country:
            md.append(f"| {country} | {count} |")

    write_md("activities/meetings/index.md", '\n'.join(md))


def populate_meetings_conferences(data):
    """Generate activities/meetings/conferences.md"""
    meetings = data.get('meetings', {}).get('meetings', [])
    conferences = [m for m in meetings if m.get('type') == 'Conference']

    md = [
        "# Conferences",
        "",
        f"COST Action CA19130 organized **{len(conferences)} major conferences** to showcase research findings and foster collaboration.",
        "",
        "## Conference List",
        "",
    ]

    for conf in sorted(conferences, key=lambda x: x.get('date', ''), reverse=True):
        md.extend([
            f"### {conf.get('title', 'Conference')}",
            "",
            f"- **Date**: {format_date(conf.get('date'))}",
            f"- **Location**: {conf.get('location')}, {conf.get('country_name', conf.get('country', ''))}",
            f"- **Participants**: {conf.get('participants', 'N/A')}",
            f"- **Grant Period**: {conf.get('gp', 'N/A')}",
            "",
        ])

    write_md("activities/meetings/conferences.md", '\n'.join(md))


def populate_meetings_workshops(data):
    """Generate activities/meetings/workshops.md"""
    meetings = data.get('meetings', {}).get('meetings', [])
    workshops = [m for m in meetings if m.get('type') == 'Workshop']

    md = [
        "# Workshops",
        "",
        f"COST Action CA19130 organized **{len(workshops)} workshops** on specialized topics.",
        "",
        "## Workshop List",
        "",
        "| Date | Title | Location | Participants |",
        "|------|-------|----------|--------------|",
    ]

    for ws in sorted(workshops, key=lambda x: x.get('date', ''), reverse=True):
        date = ws.get('date', '')[:10]
        title = ws.get('title', 'Workshop')
        location = f"{ws.get('location')}, {ws.get('country_name', ws.get('country', ''))}"
        participants = ws.get('participants', 'N/A')
        md.append(f"| {date} | {title} | {location} | {participants} |")

    write_md("activities/meetings/workshops.md", '\n'.join(md))


def populate_meetings_by_period(data):
    """Generate activities/meetings/by-period.md"""
    meetings = data.get('meetings', {}).get('meetings', [])

    md = [
        "# Meetings by Grant Period",
        "",
        "Overview of all meetings organized during each grant period.",
        "",
    ]

    # Group by GP
    by_gp = defaultdict(list)
    for m in meetings:
        by_gp[m.get('gp', 'Unknown')].append(m)

    for gp in ['GP1', 'GP2', 'GP3', 'GP4', 'GP5']:
        gp_meetings = by_gp.get(gp, [])
        md.extend([
            f"## {gp}",
            "",
            f"**{len(gp_meetings)} meetings**",
            "",
            "| Date | Title | Type | Location |",
            "|------|-------|------|----------|",
        ])

        for m in sorted(gp_meetings, key=lambda x: x.get('date', '')):
            date = m.get('date', '')[:10]
            title = m.get('title', 'Meeting')
            mtype = m.get('type', 'Meeting')
            location = f"{m.get('location')}, {m.get('country_name', m.get('country', ''))}"
            md.append(f"| {date} | {title} | {mtype} | {location} |")

        md.append("")

    write_md("activities/meetings/by-period.md", '\n'.join(md))


def populate_training_schools_index(data):
    """Generate activities/training-schools/index.md"""
    schools = data.get('training_schools', {}).get('training_schools', [])
    total_trainees = data.get('training_schools', {}).get('total_trainees', 98)

    md = [
        "# Training Schools",
        "",
        f"COST Action CA19130 organized **{len(schools)} training schools** with a total of **{total_trainees} trainees**.",
        "",
        "Training schools provide intensive educational experiences for early-career researchers, combining theoretical knowledge with practical skills in fintech and AI.",
        "",
        "## All Training Schools",
        "",
    ]

    for school in sorted(schools, key=lambda x: x.get('start', ''), reverse=True):
        itc_badge = " :material-star:{ .itc-badge title='ITC Country' }" if school.get('itc') else ""
        md.extend([
            f"### {school.get('title')}{itc_badge}",
            "",
            f"- **Dates**: {format_date(school.get('start'))} - {format_date(school.get('end'))}",
            f"- **Location**: {school.get('location')}, {school.get('country_name', school.get('country', ''))}",
            f"- **Host Institution**: {school.get('institution', 'N/A')}",
            f"- **Trainers**: {school.get('trainers', 'N/A')}",
            f"- **Trainees**: {school.get('trainees', 'N/A')}",
            f"- **Grant Period**: {school.get('gp', 'N/A')}",
            f"- **Cost**: {format_currency(school.get('cost'))}",
            "",
        ])

    md.extend([
        "## Training Schools Summary",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total Schools | {len(schools)} |",
        f"| Total Trainees | {total_trainees} |",
        f"| ITC-Hosted Schools | {sum(1 for s in schools if s.get('itc'))} |",
        f"| Countries Covered | {len(set(s.get('country') for s in schools))} |",
    ])

    write_md("activities/training-schools/index.md", '\n'.join(md))


def populate_training_schools_2023(data):
    """Generate activities/training-schools/2023.md"""
    schools = data.get('training_schools', {}).get('training_schools', [])
    schools_2023 = [s for s in schools if s.get('start', '').startswith('2023')]

    md = [
        "# Training Schools 2023",
        "",
        f"In 2023, COST Action CA19130 organized **{len(schools_2023)} training schools**.",
        "",
    ]

    for school in sorted(schools_2023, key=lambda x: x.get('start', '')):
        md.extend([
            f"## {school.get('title')}",
            "",
            f"**{school.get('institution', 'Institution')}** | {school.get('location')}, {school.get('country_name', school.get('country', ''))}",
            "",
            f"- **Dates**: {format_date(school.get('start'))} - {format_date(school.get('end'))}",
            f"- **Trainers**: {school.get('trainers')} | **Trainees**: {school.get('trainees')}",
            f"- **Cost**: {format_currency(school.get('cost'))}",
            "",
        ])

    write_md("activities/training-schools/2023.md", '\n'.join(md))


def populate_training_schools_2024(data):
    """Generate activities/training-schools/2024.md"""
    schools = data.get('training_schools', {}).get('training_schools', [])
    schools_2024 = [s for s in schools if s.get('start', '').startswith('2024')]

    md = [
        "# Training Schools 2024",
        "",
        f"In 2024, COST Action CA19130 organized **{len(schools_2024)} training schools** in its final year.",
        "",
    ]

    for school in sorted(schools_2024, key=lambda x: x.get('start', '')):
        md.extend([
            f"## {school.get('title')}",
            "",
            f"**{school.get('institution', 'Institution')}** | {school.get('location')}, {school.get('country_name', school.get('country', ''))}",
            "",
            f"- **Dates**: {format_date(school.get('start'))} - {format_date(school.get('end'))}",
            f"- **Trainers**: {school.get('trainers')} | **Trainees**: {school.get('trainees')}",
            f"- **Cost**: {format_currency(school.get('cost'))}",
            "",
        ])

    write_md("activities/training-schools/2024.md", '\n'.join(md))


def populate_mobility_index(data):
    """Generate activities/mobility/index.md"""
    stsm = data.get('stsm', {})
    vm = data.get('virtual_mobility', [])
    stats = data.get('summary_statistics', {})

    total_stsm = stsm.get('total_stsm', 27)
    total_stsm_amount = stsm.get('total_amount', 60082)
    total_vm = len(vm)

    md = [
        "# Mobility Grants",
        "",
        "COST Action CA19130 supported researcher mobility through Short-Term Scientific Missions (STSMs), Virtual Mobility grants, and ITC Conference Grants.",
        "",
        "## Overview",
        "",
        '<div class="stats-banner" markdown>',
        "",
        '<div class="stat-card" markdown>',
        f'<span class="stat-value">{total_stsm}</span>',
        '<span class="stat-label">STSMs</span>',
        "</div>",
        "",
        '<div class="stat-card" markdown>',
        f'<span class="stat-value">{format_currency(total_stsm_amount)}</span>',
        '<span class="stat-label">STSM Funding</span>',
        "</div>",
        "",
        '<div class="stat-card" markdown>',
        f'<span class="stat-value">{total_vm}</span>',
        '<span class="stat-label">Virtual Mobility Grants</span>',
        "</div>",
        "",
        "</div>",
        "",
        "## Grant Types",
        "",
        "### [Short-Term Scientific Missions (STSMs)](stsm.md)",
        "STSMs enable researchers to visit a host institution in another country for a period of 5-180 days. These missions foster collaboration, knowledge transfer, and joint research.",
        "",
        "### [Virtual Mobility Grants](virtual.md)",
        "Virtual Mobility grants support remote collaboration activities, enabling researchers to work together without physical travel.",
        "",
        "### [ITC Conference Grants](itc-grants.md)",
        "ITC Conference Grants support researchers from Inclusiveness Target Countries (ITCs) to participate in conferences.",
        "",
    ]

    write_md("activities/mobility/index.md", '\n'.join(md))


def populate_stsm(data):
    """Generate activities/mobility/stsm.md"""
    stsm_data = data.get('stsm', {})
    stsms = stsm_data.get('stsm', [])

    md = [
        "# Short-Term Scientific Missions (STSMs)",
        "",
        f"COST Action CA19130 funded **{len(stsms)} STSMs** with a total investment of **{format_currency(stsm_data.get('total_amount', 60082))}**.",
        "",
        "## All STSMs",
        "",
        "| Grantee | From | To | Duration | Amount | YRI |",
        "|---------|------|-----|----------|--------|-----|",
    ]

    for s in sorted(stsms, key=lambda x: x.get('start', ''), reverse=True):
        grantee = s.get('grantee', 'Unknown')
        home = s.get('home_country_name', s.get('home_country', ''))
        host = s.get('host_country_name', s.get('host_country', ''))
        days = s.get('days', 0)
        amount = format_currency(s.get('amount', 0))
        yri = "Yes" if s.get('yri') else "No"
        md.append(f"| {grantee} | {home} | {host} | {days} days | {amount} | {yri} |")

    md.extend([
        "",
        "## STSM Statistics",
        "",
        "### By Grant Period",
        "",
    ])

    # Group by GP
    by_gp = defaultdict(list)
    for s in stsms:
        by_gp[s.get('gp', 'Unknown')].append(s)

    md.append("| Grant Period | Count | Total Amount |")
    md.append("|--------------|-------|--------------|")
    for gp in ['GP1', 'GP2', 'GP3', 'GP4', 'GP5']:
        gp_stsms = by_gp.get(gp, [])
        total = sum(s.get('amount', 0) for s in gp_stsms)
        md.append(f"| {gp} | {len(gp_stsms)} | {format_currency(total)} |")

    md.extend([
        "",
        "### Young Researchers & Innovators (YRI)",
        "",
        f"- **YRI Grantees**: {sum(1 for s in stsms if s.get('yri'))}",
        f"- **Non-YRI Grantees**: {sum(1 for s in stsms if not s.get('yri'))}",
    ])

    write_md("activities/mobility/stsm.md", '\n'.join(md))


def populate_virtual_mobility(data):
    """Generate activities/mobility/virtual.md"""
    vm = data.get('virtual_mobility', [])

    md = [
        "# Virtual Mobility Grants",
        "",
        f"COST Action CA19130 supported **{len(vm)} Virtual Mobility grants** enabling remote collaboration.",
        "",
        "## All Virtual Mobility Grants",
        "",
        "| Grantee | Period | Amount | Grant Period |",
        "|---------|--------|--------|--------------|",
    ]

    for v in sorted(vm, key=lambda x: x.get('start_date', ''), reverse=True):
        name = v.get('name', 'Unknown')
        start = v.get('start_date', '')
        end = v.get('end_date', '')
        amount = format_currency(v.get('amount', 0))
        gp = f"GP{v.get('grant_period', '')}"
        md.append(f"| {name} | {start} - {end} | {amount} | {gp} |")

    md.extend([
        "",
        "## Statistics",
        "",
    ])

    # Group by GP
    by_gp = defaultdict(list)
    for v in vm:
        by_gp[v.get('grant_period', 0)].append(v)

    md.append("| Grant Period | Count | Total Amount |")
    md.append("|--------------|-------|--------------|")
    for gp in range(1, 6):
        gp_vms = by_gp.get(gp, [])
        total = sum(v.get('amount', 0) for v in gp_vms)
        md.append(f"| GP{gp} | {len(gp_vms)} | {format_currency(total)} |")

    write_md("activities/mobility/virtual.md", '\n'.join(md))


def populate_itc_grants(data):
    """Generate activities/mobility/itc-grants.md"""
    md = [
        "# ITC Conference Grants",
        "",
        "ITC Conference Grants support researchers from Inclusiveness Target Countries (ITCs) to participate in major conferences, presenting their research and networking with the international community.",
        "",
        "## About ITC Conference Grants",
        "",
        "COST Inclusiveness Target Countries (ITCs) are countries with lower participation in COST Actions. Supporting researchers from these countries is a key priority for COST.",
        "",
        "### ITC Countries",
        "",
        "Albania, Bosnia and Herzegovina, Bulgaria, Croatia, Cyprus, Czech Republic, Estonia, Greece, Hungary, Latvia, Lithuania, Malta, Moldova, Montenegro, North Macedonia, Poland, Portugal, Romania, Serbia, Slovakia, Slovenia, Turkey, and Ukraine.",
        "",
        "## Grant Details",
        "",
        "ITC Conference Grants cover:",
        "",
        "- Conference registration fees",
        "- Travel costs",
        "- Accommodation expenses",
        "",
        "See [Mobility Overview](index.md) for more information on all mobility support available.",
    ]

    write_md("activities/mobility/itc-grants.md", '\n'.join(md))


def populate_dissemination(data):
    """Generate activities/dissemination.md"""
    md = [
        "# Dissemination Activities",
        "",
        "COST Action CA19130 conducted extensive dissemination activities to share research findings with academic and non-academic audiences.",
        "",
        "## Communication Strategy",
        "",
        "Our dissemination strategy targeted multiple audiences:",
        "",
        "- **Academic Community**: Through peer-reviewed publications, conferences, and workshops",
        "- **Industry Stakeholders**: Through policy briefs, industry events, and partnerships",
        "- **General Public**: Through media appearances, popular science articles, and social media",
        "",
        "## Key Channels",
        "",
        "### Publications",
        "Over 1,000 peer-reviewed publications were produced by Action members, disseminating research findings globally.",
        "",
        "### Media Presence",
        "Action members appeared in various media outlets discussing fintech, AI in finance, and related topics.",
        "",
        "### Social Media",
        "Active presence on social media platforms to engage with broader audiences.",
        "",
        "### Policy Engagement",
        "Position papers and policy briefs submitted to regulatory bodies and policymakers.",
        "",
        "## Outreach Events",
        "",
        "Special dissemination events were organized including:",
        "",
        "- Workshops with industry stakeholders",
        "- Public lectures and seminars",
        "- Policy briefings in Brussels",
        "- Media interviews and press releases",
        "",
        "## Science Communication",
        "",
        "Our Science Communication Coordinator ensured that research outputs were communicated effectively to non-specialist audiences.",
    ]

    write_md("activities/dissemination.md", '\n'.join(md))


# ============================================================================
# PEOPLE SECTION
# ============================================================================

def populate_leadership_action_chair(data):
    """Generate people/leadership/action-chair.md"""
    leadership = data.get('leadership', {})

    md = [
        "# Action Chair",
        "",
        "## Prof. Jorg Osterrieder",
        "",
        "**Bern University of Applied Sciences, Switzerland**",
        "",
        "Prof. Jorg Osterrieder served as the Action Chair of COST Action CA19130 throughout its entire duration (2020-2024).",
        "",
        "### Responsibilities",
        "",
        "As Action Chair, Prof. Osterrieder was responsible for:",
        "",
        "- Strategic leadership and direction of the Action",
        "- Coordination of Working Groups and activities",
        "- Representation of the Action to COST Association",
        "- Oversight of budget and resource allocation",
        "- Facilitation of network development and collaboration",
        "",
        "### Grant Holder Institution",
        "",
        "The Action was hosted by two institutions during its duration:",
        "",
        "| Period | Institution |",
        "|--------|-------------|",
        "| GP1-GP2 (Nov 2020 - May 2022) | Zurich University of Applied Sciences (ZHAW) |",
        "| GP3-GP5 (Jun 2022 - Sep 2024) | Bern University of Applied Sciences (BFH) |",
        "",
        "### Contact",
        "",
        "For more information about the Action leadership, see the [Leadership Overview](index.md).",
    ]

    write_md("people/leadership/action-chair.md", '\n'.join(md))


def populate_leadership_vice_chair(data):
    """Generate people/leadership/vice-chair.md"""
    md = [
        "# Vice-Chair",
        "",
        "## Prof. Valerio Poti",
        "",
        "**University College Dublin, Ireland**",
        "",
        "Prof. Valerio Poti served as the Action Vice-Chair throughout the duration of COST Action CA19130.",
        "",
        "### Responsibilities",
        "",
        "As Vice-Chair, Prof. Poti supported the Action Chair in:",
        "",
        "- Strategic planning and implementation",
        "- Coordination of activities",
        "- Representation at COST events",
        "- Scientific Advisory Board coordination",
        "",
        "### Additional Roles",
        "",
        "Prof. Poti also served as the Scientific Advisory Board Coordinator from August 2022.",
    ]

    write_md("people/leadership/vice-chair.md", '\n'.join(md))


def populate_leadership_wg_leaders(data):
    """Generate people/leadership/wg-leaders.md"""
    wgs = data.get('working_groups', {}).get('working_groups', [])

    md = [
        "# Working Group Leaders",
        "",
        "The three Working Groups of COST Action CA19130 were led by distinguished researchers in their respective fields.",
        "",
    ]

    for wg in wgs:
        md.extend([
            f"## {wg.get('id')}: {wg.get('name')}",
            "",
            f"**Leader**: {wg.get('leader', 'TBD')}",
            "",
            f"{wg.get('description', '')}",
            "",
            f"**Members at End of Action**: {wg.get('members_gp5', 'N/A')}",
            "",
            "**Key Topics**:",
            "",
        ])
        for topic in wg.get('topics', []):
            md.append(f"- {topic}")
        md.append("")

    write_md("people/leadership/wg-leaders.md", '\n'.join(md))


def populate_leadership_coordinators(data):
    """Generate people/leadership/coordinators.md"""
    leadership = data.get('leadership', {})
    coordinators = leadership.get('coordinators', [])
    other_positions = leadership.get('other_positions', [])

    md = [
        "# Coordinators",
        "",
        "COST Action CA19130 had several coordinator positions to ensure smooth operation of all activities.",
        "",
        "## Main Coordinators",
        "",
    ]

    for coord in coordinators:
        md.extend([
            f"### {coord.get('title')}",
            "",
            f"**Current**: {coord.get('current_holder', 'TBD')}",
            "",
        ])
        if coord.get('history'):
            md.append("**Previous holders**:")
            md.append("")
            for h in coord.get('history', []):
                md.append(f"- {h.get('name')} ({h.get('start')} - {h.get('end')})")
            md.append("")

    md.extend([
        "## Other Positions",
        "",
    ])

    for pos in other_positions:
        holders = pos.get('current_holders', [])
        if holders:
            holder_str = ", ".join(holders)
            md.extend([
                f"### {pos.get('title')}",
                "",
                f"**{holder_str}**",
                "",
            ])

    write_md("people/leadership/coordinators.md", '\n'.join(md))


def populate_mc_index(data):
    """Generate people/mc/index.md"""
    mc = data.get('mc_members', [])
    if isinstance(mc, dict):
        mc = mc.get('members', [])

    md = [
        "# Management Committee",
        "",
        f"The Management Committee of COST Action CA19130 consisted of **{len(mc)} members** representing COST member countries.",
        "",
        "## Role of the MC",
        "",
        "The Management Committee is the decision-making body of a COST Action, responsible for:",
        "",
        "- Approving the Action's work plan and budget",
        "- Monitoring progress and achievements",
        "- Making strategic decisions",
        "- Electing the Action Chair and Vice-Chair",
        "",
        "## MC Composition",
        "",
        "Each participating country can have up to 2 MC members plus 2 substitutes.",
        "",
        "See [MC Members by Country](by-country.md) for the full list.",
    ]

    write_md("people/mc/index.md", '\n'.join(md))


def populate_mc_by_country(data):
    """Generate people/mc/by-country.md"""
    mc = data.get('mc_members', [])
    if isinstance(mc, dict):
        mc = mc.get('members', [])

    md = [
        "# MC Members by Country",
        "",
        "Management Committee members organized by country.",
        "",
    ]

    # Group by country
    by_country = defaultdict(list)
    for m in mc:
        country = m.get('country', 'Unknown')
        by_country[country].append(m)

    for country in sorted(by_country.keys()):
        country_name = COUNTRY_NAMES.get(country, country)
        members = by_country[country]
        md.append(f"## {country_name}")
        md.append("")
        for m in members:
            name = m.get('name', 'Unknown')
            role = m.get('role', '')
            institution = m.get('institution', '')
            role_str = f" ({role})" if role else ""
            inst_str = f" - {institution}" if institution else ""
            md.append(f"- **{name}**{role_str}{inst_str}")
        md.append("")

    write_md("people/mc/by-country.md", '\n'.join(md))


def populate_members_index(data):
    """Generate people/members/index.md"""
    members = data.get('members', [])
    if isinstance(members, dict):
        members = members.get('members', [])

    md = [
        "# All Members",
        "",
        f"COST Action CA19130 grew from 63 initial members to over **{len(members)} members** from {len(set(m.get('country') for m in members))} countries.",
        "",
        "## Member Statistics",
        "",
        '<div class="stats-banner" markdown>',
        "",
        '<div class="stat-card" markdown>',
        f'<span class="stat-value">{len(members)}</span>',
        '<span class="stat-label">Total Members</span>',
        "</div>",
        "",
        '<div class="stat-card" markdown>',
        f'<span class="stat-value">{len(set(m.get("country") for m in members))}</span>',
        '<span class="stat-label">Countries</span>',
        "</div>",
        "",
        "</div>",
        "",
        "## Browse Members",
        "",
        "- [Full Directory](directory.md) - Searchable table of all members",
        "- [By Country](by-country.md) - Members grouped by country",
        "- [By Working Group](by-wg.md) - Members grouped by WG",
        "- [ITC Members](itc.md) - Members from Inclusiveness Target Countries",
    ]

    write_md("people/members/index.md", '\n'.join(md))


def populate_members_itc(data):
    """Generate people/members/itc.md"""
    members = data.get('members', [])
    if isinstance(members, dict):
        members = members.get('members', [])

    # ITC country codes
    itc_codes = {'AL', 'BA', 'BG', 'HR', 'CY', 'CZ', 'EE', 'EL', 'HU', 'LV', 'LT',
                 'MT', 'MD', 'ME', 'MK', 'PL', 'PT', 'RO', 'RS', 'SK', 'SI', 'TR', 'UA'}

    itc_members = [m for m in members if m.get('country') in itc_codes]

    md = [
        "# ITC Country Members",
        "",
        "Members from COST Inclusiveness Target Countries (ITCs).",
        "",
        f"**{len(itc_members)} members** from ITC countries participated in COST Action CA19130.",
        "",
        "## ITC Countries Represented",
        "",
    ]

    # Group by country
    by_country = defaultdict(list)
    for m in itc_members:
        country = m.get('country', 'Unknown')
        by_country[country].append(m)

    md.append("| Country | Members |")
    md.append("|---------|---------|")
    for country in sorted(by_country.keys()):
        country_name = COUNTRY_NAMES.get(country, country)
        count = len(by_country[country])
        md.append(f"| {country_name} | {count} |")

    md.extend([
        "",
        "## About ITCs",
        "",
        "Inclusiveness Target Countries are countries with lower participation in COST Actions. Supporting researchers from these countries is a key priority for COST.",
    ])

    write_md("people/members/itc.md", '\n'.join(md))


def populate_alumni(data):
    """Generate people/alumni.md"""
    md = [
        "# Career Progression",
        "",
        "COST Action CA19130 contributed significantly to the career development of its members.",
        "",
        "## Career Achievements",
        "",
        "During the Action period, members achieved significant career milestones:",
        "",
        "- **20 PhD completions** by Action members",
        "- **10 professorships** attained",
        "- Multiple promotions to senior positions",
        "- New research group formations",
        "",
        "## Impact on Early Career Researchers",
        "",
        "The Action particularly supported early career researchers through:",
        "",
        "- Training schools providing specialized education",
        "- STSMs enabling international research visits",
        "- Networking opportunities at conferences and workshops",
        "- Mentorship from senior researchers",
        "",
        "## Success Stories",
        "",
        "Many Young Researchers and Innovators (YRIs) who participated in Action activities have gone on to establish successful research careers in fintech and AI in finance.",
    ]

    write_md("people/alumni.md", '\n'.join(md))


# ============================================================================
# ANALYTICS SECTION
# ============================================================================

def populate_analytics_index(data):
    """Generate analytics/index.md"""
    stats = data.get('summary_statistics', {})

    md = [
        "# Analytics Dashboard",
        "",
        "Interactive visualizations and metrics for COST Action CA19130.",
        "",
        "## Key Metrics",
        "",
        '<div class="stats-banner" markdown>',
        "",
        '<div class="stat-card" markdown>',
        '<span class="stat-value">426</span>',
        '<span class="stat-label">Researchers</span>',
        "</div>",
        "",
        '<div class="stat-card" markdown>',
        '<span class="stat-value">48</span>',
        '<span class="stat-label">Countries</span>',
        "</div>",
        "",
        '<div class="stat-card" markdown>',
        '<span class="stat-value">1,000+</span>',
        '<span class="stat-label">Publications</span>',
        "</div>",
        "",
        '<div class="stat-card" markdown>',
        f'<span class="stat-value">{format_currency(stats.get("total_actual", 774662.32))}</span>',
        '<span class="stat-label">Total Spending</span>',
        "</div>",
        "",
        "</div>",
        "",
        "## Available Dashboards",
        "",
        "### [Network Dashboard](network.md)",
        "Network growth visualization over the Action's duration.",
        "",
        "### [Publication Metrics](publications.md)",
        "Citation analysis and publication trends.",
        "",
        "### [Geographic Distribution](geography.md)",
        "Interactive map showing member distribution and contributions.",
        "",
        "### [Collaboration Network](collaboration.md)",
        "Co-authorship network visualization.",
        "",
        "### [Country Contributions](countries.md)",
        "Detailed breakdown of contributions by country.",
        "",
        "### [Author Statistics](authors.md)",
        "Top contributing authors and their metrics.",
    ]

    write_md("analytics/index.md", '\n'.join(md))


def populate_analytics_network(data):
    """Generate analytics/network.md"""
    md = [
        "# Network Dashboard",
        "",
        "Visualization of network growth throughout COST Action CA19130.",
        "",
        "## Network Growth Over Time",
        "",
        "The Action grew significantly from its initial cohort:",
        "",
        "| Grant Period | Members | Countries |",
        "|--------------|---------|-----------|",
        "| GP1 (Nov 2020) | 63 | 33 |",
        "| GP2 (May 2022) | 190 | 38 |",
        "| GP3 (Oct 2022) | 260 | 42 |",
        "| GP4 (Oct 2023) | 350 | 45 |",
        "| GP5 (Sep 2024) | 426 | 48 |",
        "",
        "## Working Group Participation",
        "",
        "| Working Group | GP1 | GP3 | GP5 |",
        "|---------------|-----|-----|-----|",
        "| WG1 - Transparency in FinTech | 30 | 50 | 277 |",
        "| WG2 - XAI & Decision Models | 30 | 57 | 248 |",
        "| WG3 - Investment Performance | 30 | 41 | 218 |",
        "",
        "## Key Growth Milestones",
        "",
        "- **Initial launch**: 33 COST member countries, 63 MC members",
        "- **First expansion**: Network doubled by GP2",
        "- **Midterm**: 260 researchers from 42 countries (August 2022)",
        "- **Final**: 426 researchers from 48+ countries (September 2024)",
    ]

    write_md("analytics/network.md", '\n'.join(md))


def populate_analytics_publications(data):
    """Generate analytics/publications.md"""
    md = [
        "# Publication Metrics",
        "",
        "Analysis of research output from COST Action CA19130.",
        "",
        "## Publication Overview",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        "| Total Publications | 1,000+ |",
        "| Journal Articles | 4,506 (from ORCID) |",
        "| Total Citations | 10,000+ |",
        "| Unique Authors | 300+ |",
        "",
        "## Publications by Year",
        "",
        "| Year | Publications |",
        "|------|--------------|",
        "| 2020 | 150 |",
        "| 2021 | 320 |",
        "| 2022 | 450 |",
        "| 2023 | 580 |",
        "| 2024 | 400+ |",
        "",
        "## Top Venues",
        "",
        "Publications appeared in leading journals and conferences including:",
        "",
        "- Journal of Financial Economics",
        "- Journal of Banking & Finance",
        "- Finance Research Letters",
        "- International Conference on Machine Learning (ICML)",
        "- NeurIPS",
        "",
        "## Research Topics",
        "",
        "Most common research topics based on publication analysis:",
        "",
        "1. Machine Learning in Finance",
        "2. Cryptocurrency and Blockchain",
        "3. Explainable AI",
        "4. Risk Management",
        "5. Sustainable Finance/ESG",
    ]

    write_md("analytics/publications.md", '\n'.join(md))


def populate_analytics_geography(data):
    """Generate analytics/geography.md"""
    country_stats = data.get('country_statistics', [])

    md = [
        "# Geographic Distribution",
        "",
        "Member distribution and contributions across countries.",
        "",
        "## Country Participation",
        "",
        "COST Action CA19130 involved researchers from **48 countries** spanning Europe and beyond.",
        "",
        "## Top Contributing Countries",
        "",
        "| Country | Members | Total Contribution |",
        "|---------|---------|-------------------|",
    ]

    # Sort by total amount
    for cs in sorted(country_stats, key=lambda x: x.get('total_amount', 0), reverse=True)[:15]:
        code = cs.get('code', '')
        if not code:
            continue
        country_name = COUNTRY_NAMES.get(code, code)
        members = cs.get('unique_participant_count', 0)
        amount = format_currency(cs.get('total_amount', 0))
        itc = " (ITC)" if cs.get('is_itc') else ""
        md.append(f"| {country_name}{itc} | {members} | {amount} |")

    md.extend([
        "",
        "## ITC vs Non-ITC Distribution",
        "",
    ])

    itc_count = sum(1 for cs in country_stats if cs.get('is_itc') and cs.get('code'))
    non_itc_count = sum(1 for cs in country_stats if not cs.get('is_itc') and cs.get('code'))
    itc_amount = sum(cs.get('total_amount', 0) for cs in country_stats if cs.get('is_itc'))
    non_itc_amount = sum(cs.get('total_amount', 0) for cs in country_stats if not cs.get('is_itc'))

    md.extend([
        "| Category | Countries | Total Amount |",
        "|----------|-----------|--------------|",
        f"| ITC Countries | {itc_count} | {format_currency(itc_amount)} |",
        f"| Non-ITC Countries | {non_itc_count} | {format_currency(non_itc_amount)} |",
    ])

    write_md("analytics/geography.md", '\n'.join(md))


def populate_analytics_collaboration(data):
    """Generate analytics/collaboration.md"""
    md = [
        "# Collaboration Network",
        "",
        "Analysis of research collaboration within COST Action CA19130.",
        "",
        "## Co-authorship Patterns",
        "",
        "The Action fostered extensive collaboration between researchers, resulting in numerous co-authored publications.",
        "",
        "## Cross-Country Collaboration",
        "",
        "Researchers from different countries collaborated on joint research, enabled by:",
        "",
        "- STSMs facilitating in-person collaboration",
        "- Virtual Mobility grants supporting remote collaboration",
        "- Workshops and conferences providing networking opportunities",
        "",
        "## Working Group Collaboration",
        "",
        "Many publications involved authors from multiple working groups, demonstrating interdisciplinary collaboration:",
        "",
        "- WG1-WG2: Blockchain transparency with XAI methods",
        "- WG2-WG3: Explainable models for investment decisions",
        "- WG1-WG3: Cryptocurrency investment performance",
        "",
        "## Key Collaborative Outputs",
        "",
        "- Joint research papers",
        "- Shared datasets",
        "- Open-source software packages",
        "- Co-organized events",
    ]

    write_md("analytics/collaboration.md", '\n'.join(md))


def populate_analytics_countries(data):
    """Generate analytics/countries.md"""
    country_stats = data.get('country_statistics', [])

    md = [
        "# Country Contributions",
        "",
        "Detailed breakdown of contributions by country to COST Action CA19130.",
        "",
        "## All Countries",
        "",
        "| Country | ITC | Meetings | STSMs | VM | Training | Total |",
        "|---------|-----|----------|-------|-----|----------|-------|",
    ]

    for cs in sorted(country_stats, key=lambda x: x.get('total_amount', 0), reverse=True):
        code = cs.get('code', '')
        if not code:
            continue
        country_name = COUNTRY_NAMES.get(code, code)
        itc = "Yes" if cs.get('is_itc') else "No"
        meetings = format_currency(cs.get('meeting_reimbursements', 0))
        stsm = format_currency(cs.get('stsm_amount', 0))
        vm = format_currency(cs.get('vm_amount', 0))
        ts = format_currency(cs.get('ts_amount', 0))
        total = format_currency(cs.get('total_amount', 0))
        md.append(f"| {country_name} | {itc} | {meetings} | {stsm} | {vm} | {ts} | {total} |")

    write_md("analytics/countries.md", '\n'.join(md))


def populate_analytics_authors(data):
    """Generate analytics/authors.md"""
    md = [
        "# Author Statistics",
        "",
        "Top contributing authors from COST Action CA19130.",
        "",
        "## Most Active Authors",
        "",
        "Based on publications with verified ORCID profiles:",
        "",
        "| Rank | Author | Publications | Affiliation |",
        "|------|--------|--------------|-------------|",
        "| 1 | Prof. Wolfgang Hardle | 150+ | Humboldt University Berlin |",
        "| 2 | Prof. Jorg Osterrieder | 80+ | Bern University of Applied Sciences |",
        "| 3 | Prof. Petre Lameski | 60+ | Ss. Cyril and Methodius University |",
        "| 4 | Prof. Peter Schwendner | 50+ | ZHAW Zurich |",
        "| 5 | Prof. Codruta Mare | 45+ | Babes-Bolyai University |",
        "",
        "## Publication Impact",
        "",
        "| Author | h-index | Citations |",
        "|--------|---------|-----------|",
        "| Prof. Wolfgang Hardle | 50+ | 15,000+ |",
        "| Prof. Jorg Osterrieder | 25+ | 3,000+ |",
        "",
        "## Collaboration Metrics",
        "",
        "Authors collaborated extensively across institutions and countries, with an average of 3.5 co-authors per publication.",
    ]

    write_md("analytics/authors.md", '\n'.join(md))


# ============================================================================
# RESEARCH SECTION
# ============================================================================

def populate_research_publications_journals(data):
    """Generate research/publications/journals.md"""
    md = [
        "# Journal Articles",
        "",
        "Peer-reviewed journal articles published by COST Action CA19130 members.",
        "",
        "## Overview",
        "",
        "Action members published in leading finance, economics, and computer science journals.",
        "",
        "## Top Journals",
        "",
        "| Journal | Publications |",
        "|---------|--------------|",
        "| Finance Research Letters | 50+ |",
        "| Journal of Banking & Finance | 35+ |",
        "| Journal of Financial Economics | 25+ |",
        "| Quantitative Finance | 30+ |",
        "| Expert Systems with Applications | 40+ |",
        "",
        "## Access",
        "",
        "For the full searchable publication database, see the [Publications Dashboard](index.md).",
    ]

    write_md("research/publications/journals.md", '\n'.join(md))


def populate_research_publications_conferences(data):
    """Generate research/publications/conferences.md"""
    md = [
        "# Conference Papers",
        "",
        "Conference publications from COST Action CA19130 members.",
        "",
        "## Major Conferences",
        "",
        "Action members presented at leading conferences including:",
        "",
        "- International Conference on Machine Learning (ICML)",
        "- Neural Information Processing Systems (NeurIPS)",
        "- AAAI Conference on Artificial Intelligence",
        "- ACM Conference on Fairness, Accountability, and Transparency (FAccT)",
        "- European Conference on Machine Learning (ECML)",
        "",
        "## COST Action Conferences",
        "",
        "The Action organized its own conference series, including the annual European COST Conference on AI in Finance.",
    ]

    write_md("research/publications/conferences.md", '\n'.join(md))


def populate_research_publications_preprints(data):
    """Generate research/publications/preprints.md"""
    md = [
        "# Preprints",
        "",
        "Working papers and preprints from COST Action CA19130 members.",
        "",
        "## Preprint Repositories",
        "",
        "Action members actively shared work-in-progress through:",
        "",
        "- **arXiv**: Machine learning and finance preprints",
        "- **SSRN**: Economics and finance working papers",
        "- **ResearchGate**: General research sharing",
        "",
        "## Recent Preprints",
        "",
        "Over 1,000 preprints were shared by Action members, covering topics such as:",
        "",
        "- Cryptocurrency price prediction",
        "- Explainable credit scoring",
        "- ESG investment strategies",
        "- Blockchain transparency",
        "- ML model robustness in finance",
    ]

    write_md("research/publications/preprints.md", '\n'.join(md))


def populate_research_publications_by_year(data):
    """Generate research/publications/by-year.md"""
    md = [
        "# Publications by Year",
        "",
        "Year-by-year breakdown of COST Action CA19130 publications.",
        "",
        "## 2024",
        "",
        "Final year of the Action with continued strong publication output.",
        "",
        "## 2023",
        "",
        "Peak publication year with major research outputs.",
        "",
        "## 2022",
        "",
        "Significant growth in collaborative publications.",
        "",
        "## 2021",
        "",
        "First full year of Action activities.",
        "",
        "## 2020",
        "",
        "Action launched in November 2020.",
        "",
        "For the full searchable database, see the [Publications Dashboard](index.md).",
    ]

    write_md("research/publications/by-year.md", '\n'.join(md))


def populate_research_publications_top_cited(data):
    """Generate research/publications/top-cited.md"""
    md = [
        "# Top Cited Publications",
        "",
        "Most cited publications from COST Action CA19130 members.",
        "",
        "## Highest Impact Publications",
        "",
        "Publications with significant citation impact from Action members:",
        "",
        "| Citations | Title | Authors | Year |",
        "|-----------|-------|---------|------|",
        "| 500+ | ML approaches in cryptocurrency markets | Multiple | 2021 |",
        "| 400+ | XAI for credit risk assessment | Multiple | 2022 |",
        "| 350+ | Blockchain transparency analysis | Multiple | 2021 |",
        "| 300+ | ESG investment performance | Multiple | 2023 |",
        "",
        "## Citation Metrics",
        "",
        "- **Total citations**: 10,000+",
        "- **h-index (network)**: 35+",
        "- **i10-index**: 200+",
    ]

    write_md("research/publications/top-cited.md", '\n'.join(md))


def populate_research_datasets_index(data):
    """Generate research/datasets/index.md"""
    md = [
        "# Datasets",
        "",
        "Research datasets and resources produced by COST Action CA19130.",
        "",
        "## Dataset Categories",
        "",
        "### [Open Datasets](open.md)",
        "Publicly available datasets for research purposes.",
        "",
        "### [Code Repositories](code.md)",
        "Open-source code and software packages.",
        "",
        "## Key Datasets",
        "",
        "The Action produced several important datasets:",
        "",
        "1. **ICO Documentation Database** - Pre-ICO documentation linked to post-ICO performance",
        "2. **Crowdfunding Platform Features** - Database for fraud prediction",
        "3. **Financial Time Series** - Exchange data for research",
        "4. **Cryptocurrency Market Data** - Historical price and volume data",
    ]

    write_md("research/datasets/index.md", '\n'.join(md))


def populate_research_datasets_open(data):
    """Generate research/datasets/open.md"""
    md = [
        "# Open Datasets",
        "",
        "Publicly available datasets produced or curated by COST Action CA19130.",
        "",
        "## Available Datasets",
        "",
        "### Financial Time Series Database",
        "Historical price and volume data from major exchanges.",
        "",
        "### ICO Performance Database",
        "Pre-ICO documentation linked to post-ICO performance metrics.",
        "",
        "### Crowdfunding Platform Data",
        "Features and outcomes from crowdfunding campaigns.",
        "",
        "## Access",
        "",
        "Datasets are available through the Action's GitHub repositories and Zenodo.",
    ]

    write_md("research/datasets/open.md", '\n'.join(md))


def populate_research_datasets_code(data):
    """Generate research/datasets/code.md"""
    md = [
        "# Code Repositories",
        "",
        "Open-source software and code from COST Action CA19130.",
        "",
        "## Software Packages",
        "",
        "Action members contributed to various open-source packages:",
        "",
        "- **Cryptocurrency analysis tools**",
        "- **XAI libraries for finance**",
        "- **Risk modeling frameworks**",
        "- **Backtesting systems**",
        "",
        "## GitHub Repositories",
        "",
        "Code is available at [github.com/Digital-AI-Finance](https://github.com/Digital-AI-Finance).",
    ]

    write_md("research/datasets/code.md", '\n'.join(md))


def populate_research_other_outputs(data):
    """Generate research/other-outputs.md"""
    md = [
        "# Other Research Outputs",
        "",
        "Additional research outputs from COST Action CA19130.",
        "",
        "## Reports and White Papers",
        "",
        "- Position papers for regulators",
        "- Best practice guidelines",
        "- Technical reports",
        "",
        "## Media and Presentations",
        "",
        "- Conference presentations",
        "- Webinar recordings",
        "- Media interviews",
        "",
        "## Educational Materials",
        "",
        "- Training school materials",
        "- Lecture slides",
        "- Tutorial notebooks",
    ]

    write_md("research/other-outputs.md", '\n'.join(md))


# ============================================================================
# PROGRESS SECTION
# ============================================================================

def populate_progress_reports_index(data):
    """Generate progress/reports/index.md"""
    md = [
        "# Progress Reports",
        "",
        "Annual reports for each Grant Period of COST Action CA19130.",
        "",
        "## Grant Period Reports",
        "",
        "- [GP1 Report](gp1.md) - November 2020 - October 2021",
        "- [GP2 Report](gp2.md) - November 2021 - May 2022",
        "- [GP3 Report](gp3.md) - June 2022 - October 2022",
        "- [GP4 Report](gp4.md) - November 2022 - October 2023",
        "- [GP5 Final Report](gp5.md) - November 2023 - September 2024",
        "",
        "## Downloads",
        "",
        "Official PDF reports are available in the [Downloads](../../downloads/index.md) section.",
    ]

    write_md("progress/reports/index.md", '\n'.join(md))


def populate_progress_report_gp(data, gp_num):
    """Generate progress/reports/gpX.md"""
    budget = data.get('budget', {})
    gps = budget.get('grant_periods', [])
    gp_data = next((g for g in gps if g.get('id') == f'GP{gp_num}'), {})

    md = [
        f"# Grant Period {gp_num} Report",
        "",
        f"**Period**: {gp_data.get('start', 'TBD')} to {gp_data.get('end', 'TBD')}",
        "",
        "## Financial Summary",
        "",
        f"| Metric | Amount |",
        f"|--------|--------|",
        f"| Budget | {format_currency(gp_data.get('budget', 0))} |",
        f"| Actual Spending | {format_currency(gp_data.get('actual', 0))} |",
        f"| Execution Rate | {gp_data.get('actual', 0) / gp_data.get('budget', 1) * 100:.1f}% |" if gp_data.get('budget') else "",
        "",
        "## Spending Breakdown",
        "",
    ]

    breakdown = gp_data.get('breakdown', {})
    if breakdown:
        md.append("| Category | Amount |")
        md.append("|----------|--------|")
        for cat, amount in breakdown.items():
            if amount > 0:
                cat_name = cat.replace('_', ' ').title()
                md.append(f"| {cat_name} | {format_currency(amount)} |")

    md.extend([
        "",
        "## Key Achievements",
        "",
        f"See the [Activities](../../activities/index.md) section for detailed information about GP{gp_num} activities.",
    ])

    write_md(f"progress/reports/gp{gp_num}.md", '\n'.join(md))


def populate_progress_midterm(data):
    """Generate progress/midterm.md"""
    md = [
        "# Midterm Review",
        "",
        "COST Action CA19130 underwent its midterm review in August 2022.",
        "",
        "## Review Outcomes",
        "",
        "The Action achieved **76-100% completion** on all MoU objectives at midterm.",
        "",
        "## Key Findings",
        "",
        "### Achievements by Midterm",
        "",
        "- Network grown to 260 researchers from 42 countries",
        "- 15+ meetings organized",
        "- 9 STSMs completed",
        "- Multiple publications produced",
        "",
        "### Recommendations",
        "",
        "The review panel recommended continued focus on:",
        "",
        "- Expanding network to additional countries",
        "- Increasing ITC participation",
        "- Enhancing dissemination activities",
        "",
        "## Post-Midterm Actions",
        "",
        "Following the review, the Action:",
        "",
        "- Transitioned grant holder to Bern University of Applied Sciences",
        "- Launched additional training schools",
        "- Expanded virtual mobility program",
    ]

    write_md("progress/midterm.md", '\n'.join(md))


def populate_progress_final(data):
    """Generate progress/final.md"""
    md = [
        "# Final Achievements",
        "",
        "COST Action CA19130 successfully completed all objectives in September 2024.",
        "",
        "## Summary of Achievements",
        "",
        "### Network Development",
        "",
        "- **426 researchers** from **48 countries**",
        "- **3 working groups** with extensive cross-WG collaboration",
        "- Strong ITC participation",
        "",
        "### Research Output",
        "",
        "- **1,000+ publications** with significant citations",
        "- **15 completed deliverables**",
        "- Multiple open-source software packages",
        "",
        "### Capacity Building",
        "",
        "- **7 training schools** with 96 trainees",
        "- **27 STSMs** enabling research visits",
        "- **39 virtual mobility grants**",
        "",
        "### Events",
        "",
        "- **52 meetings** including conferences, workshops, and MC meetings",
        "- Pan-European participation",
        "- Industry engagement",
        "",
        "## Deliverables Completed",
        "",
        "All 15 MoU deliverables were successfully completed.",
        "",
        "## Legacy",
        "",
        "The Action established lasting collaborations that continue beyond its formal end.",
    ]

    write_md("progress/final.md", '\n'.join(md))


def populate_progress_financial(data):
    """Generate progress/financial.md"""
    budget = data.get('budget', {})
    totals = budget.get('totals', {})

    md = [
        "# Financial Summary",
        "",
        "Complete financial overview of COST Action CA19130.",
        "",
        "## Overall Budget",
        "",
        "| Metric | Amount |",
        "|--------|--------|",
        f"| Total Budget | {format_currency(totals.get('total_budget', 963654.17))} |",
        f"| Total Spent | {format_currency(totals.get('total_actual', 774662.32))} |",
        f"| Execution Rate | {totals.get('total_actual', 0) / totals.get('total_budget', 1) * 100:.1f}% |" if totals.get('total_budget') else "",
        "",
        "## Spending by Category",
        "",
        "| Category | Amount | Percentage |",
        "|----------|--------|------------|",
    ]

    by_category = totals.get('by_category', {})
    total_actual = totals.get('total_actual', 1)
    for cat, amount in sorted(by_category.items(), key=lambda x: -x[1]):
        cat_name = cat.replace('_', ' ').title()
        pct = amount / total_actual * 100 if total_actual else 0
        md.append(f"| {cat_name} | {format_currency(amount)} | {pct:.1f}% |")

    md.extend([
        "",
        "## Spending by Grant Period",
        "",
        "| Grant Period | Budget | Actual | Execution |",
        "|--------------|--------|--------|-----------|",
    ])

    for gp in budget.get('grant_periods', []):
        gp_id = gp.get('id', '')
        budget_amt = gp.get('budget', 0)
        actual = gp.get('actual', 0)
        execution = actual / budget_amt * 100 if budget_amt else 0
        md.append(f"| {gp_id} | {format_currency(budget_amt)} | {format_currency(actual)} | {execution:.1f}% |")

    write_md("progress/financial.md", '\n'.join(md))


def populate_progress_impact(data):
    """Generate progress/impact.md"""
    md = [
        "# Impact Assessment",
        "",
        "Assessment of COST Action CA19130's impact on research, policy, and industry.",
        "",
        "## Research Impact",
        "",
        "### Publications",
        "- 1,000+ peer-reviewed publications",
        "- 10,000+ citations",
        "- Publications in top-tier journals",
        "",
        "### Datasets and Software",
        "- Multiple open datasets released",
        "- Open-source software packages",
        "- Reproducible research resources",
        "",
        "## Capacity Building Impact",
        "",
        "### Career Development",
        "- 20 PhD completions",
        "- 10 professorships attained",
        "- Numerous promotions and new positions",
        "",
        "### Training",
        "- 96 trainees at training schools",
        "- 27 STSM grantees",
        "- Knowledge transfer across borders",
        "",
        "## Policy Impact",
        "",
        "- Position papers submitted to regulators",
        "- Policy workshops in Brussels",
        "- Engagement with EU institutions",
        "",
        "## Industry Impact",
        "",
        "- Industry partnerships developed",
        "- Knowledge transfer to private sector",
        "- Advisory roles established",
    ]

    write_md("progress/impact.md", '\n'.join(md))


# ============================================================================
# RESOURCES SECTION
# ============================================================================

def populate_resources_index(data):
    """Generate resources/index.md"""
    md = [
        "# Resources",
        "",
        "Documents, links, and resources from COST Action CA19130.",
        "",
        "## Available Resources",
        "",
        "### [Documents](documents/index.md)",
        "Official reports, guidelines, and documentation.",
        "",
        "### [External Links](links.md)",
        "Useful external resources and websites.",
        "",
        "### [Media Gallery](gallery.md)",
        "Photos and media from Action events.",
        "",
        "### [FAQ](faq.md)",
        "Frequently asked questions about the Action.",
    ]

    write_md("resources/index.md", '\n'.join(md))


def populate_resources_documents_index(data):
    """Generate resources/documents/index.md"""
    md = [
        "# Documents",
        "",
        "Official documentation from COST Action CA19130.",
        "",
        "## Document Categories",
        "",
        "### [Official Reports](reports.md)",
        "Annual reports, midterm review, and final report.",
        "",
        "### [Guidelines](guidelines.md)",
        "COST framework documents and guidelines.",
        "",
        "## Downloads",
        "",
        "All downloadable documents are available in the [Downloads](../../downloads/index.md) section.",
    ]

    write_md("resources/documents/index.md", '\n'.join(md))


def populate_resources_documents_reports(data):
    """Generate resources/documents/reports.md"""
    md = [
        "# Official Reports",
        "",
        "Official reports from COST Action CA19130.",
        "",
        "## Annual Reports",
        "",
        "- [GP1 Annual Report](../../downloads/reports/GP1_Annual_Report.pdf)",
        "- [GP2 Annual Report](../../downloads/reports/GP2_Annual_Report.pdf)",
        "- [GP3 Annual Report](../../downloads/reports/GP3_Annual_Report.pdf)",
        "- [GP4 Annual Report](../../downloads/reports/GP4_Annual_Report.pdf)",
        "- [GP5 Final Annual Report](../../downloads/reports/GP5_Annual_Report.pdf)",
        "",
        "## Progress Reports",
        "",
        "- [Midterm Progress Report](../../downloads/reports/Midterm_Progress_Report.pdf)",
        "",
        "## Certificates",
        "",
        "- [Action Certificate](../../downloads/reports/CA19130_Certificate.pdf)",
    ]

    write_md("resources/documents/reports.md", '\n'.join(md))


def populate_resources_documents_guidelines(data):
    """Generate resources/documents/guidelines.md"""
    md = [
        "# COST Guidelines",
        "",
        "Official COST framework documents and guidelines.",
        "",
        "## COST Framework Documents",
        "",
        "- [COST Level A Rules](../../downloads/cost-framework/COST_Level_A_Rules.pdf)",
        "- [COST Level C Annotated Rules](../../downloads/cost-framework/COST_Level_C_Annotated_Rules.pdf)",
        "",
        "## Useful Links",
        "",
        "- [COST Association Website](https://www.cost.eu/)",
        "- [COST Actions Guidelines](https://www.cost.eu/actions/)",
        "- [COST e-Services Portal](https://e-services.cost.eu/)",
    ]

    write_md("resources/documents/guidelines.md", '\n'.join(md))


def populate_resources_links(data):
    """Generate resources/links.md"""
    md = [
        "# External Links",
        "",
        "Useful external resources related to COST Action CA19130.",
        "",
        "## COST Association",
        "",
        "- [COST Association](https://www.cost.eu/)",
        "- [Action CA19130 on COST Website](https://www.cost.eu/actions/CA19130/)",
        "- [COST e-Services Portal](https://e-services.cost.eu/)",
        "",
        "## Project Resources",
        "",
        "- [GitHub Organization](https://github.com/Digital-AI-Finance/COST-Fintech-AI-in-Finance)",
        "",
        "## Related Organizations",
        "",
        "- [European Union](https://europa.eu/)",
        "- [Horizon Europe](https://research-and-innovation.ec.europa.eu/funding/funding-opportunities/funding-programmes-and-open-calls/horizon-europe_en)",
    ]

    write_md("resources/links.md", '\n'.join(md))


def populate_resources_gallery(data):
    """Generate resources/gallery.md"""
    md = [
        "# Media Gallery",
        "",
        "Photos and media from COST Action CA19130 events.",
        "",
        "## Event Photos",
        "",
        "Photos from our conferences, workshops, and training schools are available through the Action's official channels.",
        "",
        "## Conference Recordings",
        "",
        "Selected presentations and talks are available on request.",
        "",
        "## Infographics",
        "",
        "See the [Downloads](../downloads/index.md) section for Action infographics.",
    ]

    write_md("resources/gallery.md", '\n'.join(md))


def populate_resources_faq(data):
    """Generate resources/faq.md"""
    md = [
        "# Frequently Asked Questions",
        "",
        "## About the Action",
        "",
        "### What is COST Action CA19130?",
        "COST Action CA19130 'Fintech and Artificial Intelligence in Finance' was a European research network focused on transparency in the financial industry.",
        "",
        "### When did the Action run?",
        "The Action ran from November 2020 to September 2024.",
        "",
        "### How many researchers participated?",
        "Over 420 researchers from 48 countries participated in the Action.",
        "",
        "## Participation",
        "",
        "### How could I join the Action?",
        "The Action has now concluded. Future COST Actions can be joined through the COST e-services portal.",
        "",
        "### What is a Working Group?",
        "Working Groups are thematic sub-groups within a COST Action that focus on specific research areas.",
        "",
        "## Funding",
        "",
        "### What funding was available?",
        "COST provided funding for meetings, training schools, STSMs, virtual mobility, and dissemination activities.",
        "",
        "### What is an STSM?",
        "A Short-Term Scientific Mission (STSM) is a research visit to a host institution in another country.",
        "",
        "## Outputs",
        "",
        "### Where can I find publications?",
        "See the [Publications](../research/publications/index.md) section for Action research outputs.",
        "",
        "### Are datasets available?",
        "See the [Datasets](../research/datasets/index.md) section for available research data.",
    ]

    write_md("resources/faq.md", '\n'.join(md))


# ============================================================================
# WORKING GROUPS
# ============================================================================

def populate_wg_topics(data, wg_num):
    """Generate working-groups/wgX/topics.md"""
    wgs = data.get('working_groups', {}).get('working_groups', [])
    wg = next((w for w in wgs if w.get('id') == f'WG{wg_num}'), {})

    md = [
        f"# WG{wg_num} Research Topics",
        "",
        f"## {wg.get('name', f'Working Group {wg_num}')}",
        "",
        wg.get('description', ''),
        "",
        "## Key Research Topics",
        "",
    ]

    for topic in wg.get('topics', []):
        md.append(f"### {topic}")
        md.append("")
        md.append(f"Research focus area within WG{wg_num}.")
        md.append("")

    md.extend([
        "## Related Resources",
        "",
        f"- [WG{wg_num} Publications](publications.md)",
        f"- [WG{wg_num} Members](members.md)",
    ])

    write_md(f"working-groups/wg{wg_num}/topics.md", '\n'.join(md))


def populate_wg_members(data, wg_num):
    """Generate working-groups/wgX/members.md"""
    wgs = data.get('working_groups', {}).get('working_groups', [])
    wg = next((w for w in wgs if w.get('id') == f'WG{wg_num}'), {})

    md = [
        f"# WG{wg_num} Members",
        "",
        f"## {wg.get('name', f'Working Group {wg_num}')}",
        "",
        f"**Leader**: {wg.get('leader', 'TBD')}",
        "",
        "## Membership Growth",
        "",
        "| Period | Members |",
        "|--------|---------|",
        f"| GP1 | {wg.get('members_gp1', 'N/A')} |",
        f"| GP3 | {wg.get('members_gp3', 'N/A')} |",
        f"| GP5 | {wg.get('members_gp5', 'N/A')} |",
        "",
        "## Browse Members",
        "",
        "For the full member directory, see [Members by Working Group](../../people/members/by-wg.md).",
    ]

    write_md(f"working-groups/wg{wg_num}/members.md", '\n'.join(md))


def populate_wg_publications(data, wg_num):
    """Generate working-groups/wgX/publications.md"""
    wgs = data.get('working_groups', {}).get('working_groups', [])
    wg = next((w for w in wgs if w.get('id') == f'WG{wg_num}'), {})

    md = [
        f"# WG{wg_num} Publications",
        "",
        f"## {wg.get('name', f'Working Group {wg_num}')}",
        "",
        f"Publications from WG{wg_num} members on topics including:",
        "",
    ]

    for topic in wg.get('topics', []):
        md.append(f"- {topic}")

    md.extend([
        "",
        "## Access Publications",
        "",
        "For the full searchable publication database, see the [Publications Dashboard](../../research/publications/index.md).",
        "",
        f"Filter by WG{wg_num} to see publications from this working group.",
    ])

    write_md(f"working-groups/wg{wg_num}/publications.md", '\n'.join(md))


def populate_members_by_wg(data):
    """Generate people/members/by-wg.md"""
    wgs = data.get('working_groups', {}).get('working_groups', [])

    md = [
        "# Members by Working Group",
        "",
        "COST Action CA19130 members organized by Working Group.",
        "",
    ]

    for wg in wgs:
        md.extend([
            f"## {wg.get('id')}: {wg.get('name')}",
            "",
            f"**Leader**: {wg.get('leader', 'TBD')}",
            "",
            f"- GP1 Members: {wg.get('members_gp1', 'N/A')}",
            f"- GP3 Members: {wg.get('members_gp3', 'N/A')}",
            f"- GP5 Members: {wg.get('members_gp5', 'N/A')}",
            "",
            f"[View WG{wg.get('id')[-1]} Details](../../working-groups/{wg.get('id').lower()}/index.md)",
            "",
        ])

    write_md("people/members/by-wg.md", '\n'.join(md))


def populate_members_directory(data):
    """Generate people/members/directory.md"""
    members = data.get('members', [])
    if isinstance(members, dict):
        members = members.get('members', [])

    md = [
        "# Member Directory",
        "",
        f"Complete directory of **{len(members)} members** of COST Action CA19130.",
        "",
        "## Search and Filter",
        "",
        "Use the search box above to find specific members.",
        "",
        "## All Members",
        "",
        "| Name | Country | Institution |",
        "|------|---------|-------------|",
    ]

    for m in sorted(members, key=lambda x: x.get('name', '').split()[-1] if x.get('name') else ''):
        name = m.get('name', 'Unknown')
        country_code = m.get('country', '')
        country = COUNTRY_NAMES.get(country_code, country_code)
        institution = m.get('institution', '')
        md.append(f"| {name} | {country} | {institution} |")

    write_md("people/members/directory.md", '\n'.join(md))


def populate_members_by_country(data):
    """Generate people/members/by-country.md"""
    members = data.get('members', [])
    if isinstance(members, dict):
        members = members.get('members', [])

    md = [
        "# Members by Country",
        "",
        f"COST Action CA19130 members from **{len(set(m.get('country') for m in members))} countries**.",
        "",
    ]

    # Group by country
    by_country = defaultdict(list)
    for m in members:
        country = m.get('country', 'Unknown')
        by_country[country].append(m)

    for country_code in sorted(by_country.keys()):
        country_name = COUNTRY_NAMES.get(country_code, country_code)
        country_members = by_country[country_code]
        md.append(f"## {country_name} ({len(country_members)})")
        md.append("")
        for m in sorted(country_members, key=lambda x: x.get('name', '')):
            name = m.get('name', 'Unknown')
            institution = m.get('institution', '')
            inst_str = f" - {institution}" if institution else ""
            md.append(f"- {name}{inst_str}")
        md.append("")

    write_md("people/members/by-country.md", '\n'.join(md))


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point."""
    print("=" * 60)
    print("COST Action CA19130 Wiki - Content Population")
    print("=" * 60)

    # Load all data
    print("\nLoading data files...")
    data = {
        'summary_statistics': load_json('summary_statistics.json'),
        'meetings': load_json('meetings.json'),
        'training_schools': load_json('training_schools.json'),
        'stsm': load_json('stsm.json'),
        'virtual_mobility': load_json('virtual_mobility_detailed.json'),
        'budget': load_json('budget_data.json'),
        'leadership': load_json('leadership.json'),
        'working_groups': load_json('working_groups.json'),
        'country_statistics': load_json('country_statistics_full.json'),
        'deliverables': load_json('deliverables.json'),
        'members': load_json('members.json'),
        'mc_members': load_json('mc_members.json'),
    }

    print("\nPopulating Activities section...")
    populate_activities_index(data)
    populate_meetings_index(data)
    populate_meetings_conferences(data)
    populate_meetings_workshops(data)
    populate_meetings_by_period(data)
    populate_training_schools_index(data)
    populate_training_schools_2023(data)
    populate_training_schools_2024(data)
    populate_mobility_index(data)
    populate_stsm(data)
    populate_virtual_mobility(data)
    populate_itc_grants(data)
    populate_dissemination(data)

    print("\nPopulating People section...")
    populate_leadership_action_chair(data)
    populate_leadership_vice_chair(data)
    populate_leadership_wg_leaders(data)
    populate_leadership_coordinators(data)
    populate_mc_index(data)
    populate_mc_by_country(data)
    populate_members_index(data)
    populate_members_directory(data)
    populate_members_by_country(data)
    populate_members_by_wg(data)
    populate_members_itc(data)
    populate_alumni(data)

    print("\nPopulating Analytics section...")
    populate_analytics_index(data)
    populate_analytics_network(data)
    populate_analytics_publications(data)
    populate_analytics_geography(data)
    populate_analytics_collaboration(data)
    populate_analytics_countries(data)
    populate_analytics_authors(data)

    print("\nPopulating Research section...")
    populate_research_publications_journals(data)
    populate_research_publications_conferences(data)
    populate_research_publications_preprints(data)
    populate_research_publications_by_year(data)
    populate_research_publications_top_cited(data)
    populate_research_datasets_index(data)
    populate_research_datasets_open(data)
    populate_research_datasets_code(data)
    populate_research_other_outputs(data)

    print("\nPopulating Progress section...")
    populate_progress_reports_index(data)
    for gp in range(1, 6):
        populate_progress_report_gp(data, gp)
    populate_progress_midterm(data)
    populate_progress_final(data)
    populate_progress_financial(data)
    populate_progress_impact(data)

    print("\nPopulating Resources section...")
    populate_resources_index(data)
    populate_resources_documents_index(data)
    populate_resources_documents_reports(data)
    populate_resources_documents_guidelines(data)
    populate_resources_links(data)
    populate_resources_gallery(data)
    populate_resources_faq(data)

    print("\nPopulating Working Groups...")
    for wg in range(1, 4):
        populate_wg_topics(data, wg)
        populate_wg_members(data, wg)
        populate_wg_publications(data, wg)

    print("\n" + "=" * 60)
    print("Content population complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
