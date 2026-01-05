"""
COST Action CA19130 Wiki - Member Profile Generator

Generates individual markdown profile pages for all 426 members.
Merges data from multiple JSON sources.

Usage:
    python generate_member_profiles.py
"""

import json
import re
import unicodedata
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Paths
REPO_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = REPO_ROOT / "data"
DOCS_DIR = Path(__file__).parent.parent / "docs"
PROFILES_DIR = DOCS_DIR / "people" / "profiles"

# Color palette for avatar backgrounds (rotate through)
AVATAR_COLORS = [
    "#5B2D8A", "#2B5F9E", "#00A0B0", "#E87722",
    "#7AB800", "#7B4DAA", "#4B7FBE", "#D62728"
]


def load_json(filepath):
    """Load a JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load {filepath}: {e}")
        return None


def normalize_name(name):
    """Normalize a name for matching (handles unicode, titles, etc.)."""
    if not name:
        return ""
    # Normalize unicode (remove accents/umlauts for matching)
    name = unicodedata.normalize('NFKD', name)
    name = name.encode('ASCII', 'ignore').decode('ASCII')
    # Remove titles
    name = re.sub(r'\b(Prof|Dr|Mr|Ms|Mrs|Assoc|Assist)\b\.?\s*', '', name, flags=re.IGNORECASE)
    # Handle "Last, First" format
    if ',' in name:
        parts = name.split(',', 1)
        name = f"{parts[1].strip()} {parts[0].strip()}"
    # Remove extra spaces
    name = ' '.join(name.split())
    return name.lower().strip()


def generate_slug(name):
    """Generate a URL-safe slug from a name."""
    # Normalize unicode characters
    name = unicodedata.normalize('NFKD', name)
    name = name.encode('ASCII', 'ignore').decode('ASCII')
    # Lowercase and replace spaces
    slug = name.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug


def get_initials(name):
    """Get initials from a name."""
    parts = name.split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    elif len(parts) == 1:
        return parts[0][:2].upper()
    return "??"


def get_avatar_color(name):
    """Get a consistent avatar color for a name."""
    hash_val = sum(ord(c) for c in name) % len(AVATAR_COLORS)
    return AVATAR_COLORS[hash_val]


def get_country_flag_emoji(country):
    """Get country flag emoji (placeholder - actual implementation would use country codes)."""
    # Just return the country name for now
    return country


def load_all_data():
    """Load all data sources."""
    data = {}

    # Core member data
    data['members'] = load_json(DATA_DIR / "members.json") or []
    data['mc_members'] = load_json(DATA_DIR / "mc_members.json") or []
    data['leadership'] = load_json(DATA_DIR / "leadership.json") or {}
    data['wg1_members'] = load_json(DATA_DIR / "wg1_members.json") or []
    data['wg2_members'] = load_json(DATA_DIR / "wg2_members.json") or []
    data['wg3_members'] = load_json(DATA_DIR / "wg3_members.json") or []

    # Publication data (load only validated ORCIDs for now)
    data['validated_orcids'] = load_json(DATA_DIR / "validated_orcids.json") or {}

    # Try to load ORCID publications
    orcid_pubs = load_json(DATA_DIR / "orcid_publications.json")
    if orcid_pubs:
        data['orcid_publications'] = orcid_pubs
    else:
        data['orcid_publications'] = {"publications": [], "metadata": {}}

    return data


def get_leadership_roles(member_name, leadership_data):
    """Get leadership positions for a member."""
    roles = []
    normalized = normalize_name(member_name)

    if not leadership_data:
        return roles

    # Core leadership
    for pos in leadership_data.get('core_leadership', []):
        if normalize_name(pos.get('current_holder', '')) == normalized:
            roles.append({
                'title': pos['title'],
                'level': 'core',
                'badge_class': 'badge-chair' if 'Chair' in pos['title'] else 'badge-coordinator'
            })

    # WG Leaders
    for wg in leadership_data.get('working_groups', []):
        if normalize_name(wg.get('leader', '')) == normalized:
            roles.append({
                'title': f"WG{wg['number']} Leader",
                'level': 'wg',
                'badge_class': 'badge-wg-leader'
            })

    # Coordinators
    for coord in leadership_data.get('coordinators', []):
        if normalize_name(coord.get('current_holder', '')) == normalized:
            roles.append({
                'title': coord['title'],
                'level': 'coordinator',
                'badge_class': 'badge-coordinator',
                'start_date': coord.get('start_date')
            })

    # Other positions
    for pos in leadership_data.get('other_positions', []):
        for holder in pos.get('current_holders', []):
            if normalize_name(holder) == normalized:
                roles.append({
                    'title': pos['title'],
                    'level': 'other',
                    'badge_class': 'badge-coordinator'
                })

    return roles


def get_member_publications(orcid, orcid_publications):
    """Get publications for a member by ORCID."""
    if not orcid or not orcid_publications:
        return []

    pubs = []
    for pub in orcid_publications.get('publications', []):
        cost_author = pub.get('cost_author', {})
        if cost_author.get('orcid') == orcid:
            pubs.append(pub)

    return sorted(pubs, key=lambda x: x.get('year', 0), reverse=True)


def generate_profile_markdown(member, data):
    """Generate markdown content for a member profile."""
    name = member.get('name', 'Unknown')
    slug = generate_slug(name)
    initials = get_initials(name)
    color = get_avatar_color(name)

    # Get additional data
    roles = get_leadership_roles(name, data.get('leadership'))
    publications = get_member_publications(member.get('orcid'), data.get('orcid_publications'))

    # Count working groups
    wg_count = sum([
        1 if member.get('wg1') else 0,
        1 if member.get('wg2') else 0,
        1 if member.get('wg3') else 0
    ])

    # Build markdown
    md = []

    # Header with avatar and badges
    md.append(f"# {name}")
    md.append("")

    # Profile header section
    md.append('<div class="profile-header" markdown>')
    md.append(f'<div class="avatar-circle" style="background: {color};">')
    md.append(f'<span>{initials}</span>')
    md.append('</div>')
    md.append('<div class="profile-info" markdown>')
    md.append("")
    md.append(f"**{member.get('affiliation', 'Affiliation not specified')}**")
    md.append("")
    md.append(f"{member.get('country', 'Country not specified')}")
    md.append("")

    # ORCID link
    if member.get('orcid'):
        md.append(f'<a href="https://orcid.org/{member["orcid"]}" target="_blank">')
        md.append(f'<img src="https://orcid.org/sites/default/files/images/orcid_16x16.png" alt="ORCID"> {member["orcid"]}</a>')
        md.append("")

    # Badges
    badges = []
    for role in roles:
        badges.append(f'<span class="{role["badge_class"]}">{role["title"]}</span>')
    if member.get('mc'):
        badges.append('<span class="badge-mc">MC Member</span>')
    if member.get('itc'):
        badges.append('<span class="badge-itc">ITC</span>')

    if badges:
        md.append('<div class="badges">')
        md.append(' '.join(badges))
        md.append('</div>')

    md.append('</div>')
    md.append('</div>')
    md.append("")

    # Quick stats
    md.append("## Quick Stats")
    md.append("")
    md.append('<div class="metrics-grid" markdown>')

    md.append('<div class="metric-card" markdown>')
    md.append(f'<span class="metric-value">{len(publications)}</span>')
    md.append('<span class="metric-label">Publications</span>')
    md.append('</div>')

    md.append('<div class="metric-card" markdown>')
    md.append(f'<span class="metric-value">{wg_count}</span>')
    md.append('<span class="metric-label">Working Groups</span>')
    md.append('</div>')

    md.append('<div class="metric-card" markdown>')
    md.append(f'<span class="metric-value">{len(roles)}</span>')
    md.append('<span class="metric-label">Leadership Roles</span>')
    md.append('</div>')

    md.append('<div class="metric-card" markdown>')
    orcid_status = "Yes" if member.get('orcid') else "No"
    md.append(f'<span class="metric-value">{orcid_status}</span>')
    md.append('<span class="metric-label">ORCID Linked</span>')
    md.append('</div>')

    md.append('</div>')
    md.append("")

    # Affiliation
    md.append("## Affiliation")
    md.append("")
    md.append(f"**Institution**: {member.get('affiliation', 'Not specified')}")
    md.append("")
    md.append(f"**Country**: {member.get('country', 'Not specified')}")
    md.append("")

    # Working Groups
    md.append("## Working Group Memberships")
    md.append("")
    wg_list = []
    if member.get('wg1'):
        wg_list.append("- [WG1: Transparency in FinTech](../../working-groups/wg1/)")
    if member.get('wg2'):
        wg_list.append("- [WG2: XAI & Decision Models](../../working-groups/wg2/)")
    if member.get('wg3'):
        wg_list.append("- [WG3: Investment Performance](../../working-groups/wg3/)")

    if wg_list:
        md.extend(wg_list)
    else:
        md.append("*No working group memberships recorded.*")
    md.append("")

    # Leadership Roles
    if roles:
        md.append("## Leadership Positions")
        md.append("")
        for role in roles:
            if role.get('start_date'):
                md.append(f"- **{role['title']}** (since {role['start_date']})")
            else:
                md.append(f"- **{role['title']}**")
        md.append("")

    # Publications
    if publications:
        md.append("## Publications")
        md.append("")
        md.append(f"*Showing {len(publications)} publications from ORCID profile.*")
        md.append("")

        # Group by year
        by_year = defaultdict(list)
        for pub in publications:
            year = pub.get('year', 'Unknown')
            by_year[year].append(pub)

        for year in sorted(by_year.keys(), reverse=True):
            md.append(f"### {year}")
            md.append("")
            for pub in by_year[year]:
                title = pub.get('title', 'Untitled')
                doi = pub.get('doi', '')
                venue = pub.get('venue', '')
                pub_type = pub.get('type', 'article')

                md.append(f"- **{title}**")
                if venue:
                    md.append(f"  - *{venue}*")
                if doi:
                    md.append(f"  - [DOI]({doi})")
                md.append("")
    else:
        md.append("## Publications")
        md.append("")
        if member.get('orcid'):
            md.append(f"*View full publication list on [ORCID](https://orcid.org/{member['orcid']}).*")
        else:
            md.append("*No ORCID profile linked. Publications not available.*")
        md.append("")

    # Navigation
    md.append("---")
    md.append("")
    md.append("## Navigation")
    md.append("")
    country = member.get('country', 'Unknown')
    md.append(f"- [All members from {country}](../members/by-country.md)")
    md.append("- [Member Directory](../members/directory.md)")
    md.append("- [Back to People](../index.md)")
    md.append("")

    return '\n'.join(md)


def generate_all_profiles(data):
    """Generate profile pages for all members."""
    members = data.get('members', [])

    if not members:
        print("No members found!")
        return

    # Create profiles directory
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)

    # Track slugs to handle duplicates
    slug_counts = defaultdict(int)
    generated = 0
    skipped = 0

    for member in members:
        name = member.get('name', '').strip()

        # Skip invalid entries
        if not name or name.lower() in ['aaa aaa', 'test', 'unknown']:
            skipped += 1
            continue

        # Generate slug
        slug = generate_slug(name)
        if not slug:
            skipped += 1
            continue

        # Handle duplicates
        slug_counts[slug] += 1
        if slug_counts[slug] > 1:
            # Add country code for disambiguation
            country_code = member.get('country', 'unknown')[:2].lower()
            slug = f"{slug}-{country_code}"

        # Generate markdown
        content = generate_profile_markdown(member, data)

        # Write file
        filepath = PROFILES_DIR / f"{slug}.md"
        filepath.write_text(content, encoding='utf-8')
        generated += 1

    print(f"Generated {generated} profile pages")
    print(f"Skipped {skipped} invalid entries")
    return generated


def generate_profiles_index(data):
    """Generate the profiles index page."""
    members = data.get('members', [])

    # Filter valid members
    valid_members = [m for m in members if m.get('name') and m['name'].lower() not in ['aaa aaa', 'test', 'unknown']]

    # Sort alphabetically
    valid_members.sort(key=lambda x: x.get('name', '').lower())

    md = []
    md.append("# Member Profiles")
    md.append("")
    md.append(f"Browse individual profiles for all {len(valid_members)} COST Action CA19130 members.")
    md.append("")
    md.append("## All Members (A-Z)")
    md.append("")

    # Group by first letter
    by_letter = defaultdict(list)
    for member in valid_members:
        first_letter = member['name'][0].upper()
        by_letter[first_letter].append(member)

    for letter in sorted(by_letter.keys()):
        md.append(f"### {letter}")
        md.append("")
        for member in by_letter[letter]:
            slug = generate_slug(member['name'])
            country = member.get('country', 'Unknown')
            affiliation = member.get('affiliation', '')
            md.append(f"- [{member['name']}]({slug}.md) - {affiliation} ({country})")
        md.append("")

    # Write index
    index_path = PROFILES_DIR / "index.md"
    index_path.write_text('\n'.join(md), encoding='utf-8')
    print("Generated profiles index page")


def main():
    """Main entry point."""
    print("Loading data...")
    data = load_all_data()

    print(f"Found {len(data.get('members', []))} members")
    print(f"Found {len(data.get('orcid_publications', {}).get('publications', []))} publications")

    print("\nGenerating member profiles...")
    count = generate_all_profiles(data)

    print("\nGenerating profiles index...")
    generate_profiles_index(data)

    print(f"\nDone! Generated {count} profile pages in {PROFILES_DIR}")


if __name__ == "__main__":
    main()
