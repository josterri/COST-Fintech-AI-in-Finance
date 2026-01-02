"""
Process COST Action CA19130 member data from Excel to JSON for GitHub Pages.
"""
import pandas as pd
import json
from pathlib import Path

def extract_country_name(country_str):
    """Extract country name from format 'Country Name (XX)'"""
    if pd.isna(country_str):
        return 'Unknown'
    # Remove the country code in parentheses
    if '(' in str(country_str):
        return str(country_str).split('(')[0].strip()
    return str(country_str).strip()

def main():
    # Paths
    script_dir = Path(__file__).parent
    wg_file = script_dir / 'working_groups_members' / 'CA19130-WG-members.xlsx'
    output_file = script_dir / 'data' / 'members.json'

    # Read WG members data
    print(f"Reading: {wg_file}")
    df = pd.read_excel(wg_file)

    print(f"Total rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")

    # Process members
    members = []
    for _, row in df.iterrows():
        first_name = str(row.get('First Name', '')).strip() if pd.notna(row.get('First Name')) else ''
        last_name = str(row.get('Last Name', '')).strip() if pd.notna(row.get('Last Name')) else ''

        if not first_name and not last_name:
            continue

        member = {
            'name': f"{first_name} {last_name}".strip(),
            'affiliation': str(row.get('Affiliation', '')).strip() if pd.notna(row.get('Affiliation')) else None,
            'country': extract_country_name(row.get('Country')),
            'wg1': str(row.get('WG1. Transparency in FinTech', '')).lower() == 'y',
            'wg2': str(row.get('WG2. Transparent versus Black Box Decision-Support Models in the Financial Industry', '')).lower() == 'y',
            'wg3': str(row.get('WG3. Transparency into Investment Product Performance for Clients', '')).lower() == 'y',
            'mc': str(row.get('MC Membership Status', '')).lower() == 'member',
            'itc': str(row.get('ITC', '')).lower() == 'y',
            'orcid': str(row.get('Orcid', '')).strip() if pd.notna(row.get('Orcid')) else None,
            'gender': str(row.get('Gender', '')).strip() if pd.notna(row.get('Gender')) else None,
        }

        members.append(member)

    # Sort by name
    members.sort(key=lambda x: x['name'].lower())

    # Save JSON
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(members, f, indent=2, ensure_ascii=False)

    print(f"\nProcessed {len(members)} members")
    print(f"Output saved to: {output_file}")

    # Statistics
    print("\n=== Statistics ===")
    print(f"WG1 members: {sum(1 for m in members if m['wg1'])}")
    print(f"WG2 members: {sum(1 for m in members if m['wg2'])}")
    print(f"WG3 members: {sum(1 for m in members if m['wg3'])}")
    print(f"MC members: {sum(1 for m in members if m['mc'])}")
    print(f"ITC members: {sum(1 for m in members if m['itc'])}")

    countries = set(m['country'] for m in members)
    print(f"Countries: {len(countries)}")

if __name__ == '__main__':
    main()
