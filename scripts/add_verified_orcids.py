"""
Add verified ORCIDs to the COST Action Excel file.
"""

import sys
import io
from pathlib import Path
from datetime import datetime
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

ORCIDS_TO_ADD = [
    ("MIRJANA IVANOVIC", "0000-0003-1946-0384"),
    ("Andreas Gregoriades", "0000-0002-7422-1514"),
    ("Alessia Paccagnini", "0000-0002-2421-7242"),
    ("Simon Trimborn", "0000-0003-3745-4164"),
    ("Jelena Poljaševic", "0000-0002-6891-4875"),
    ("Martina Solenicki", "0000-0001-6380-1700"),
    ("Ana Ivanisevic Hernaus", "0000-0003-0370-5543"),
    ("Paraskevi Tsoutsa", "0000-0003-0019-1145"),
    ("Mesut Karakaş", "0000-0002-3695-2105"),
    ("Ioana Birlan", "0009-0007-7097-3341"),
    ("Vlad Bolovăneanu", "0009-0000-3660-4410"),
    ("Emmanuel Eyiah-Donkor", "0000-0003-1323-1716"),
    ("Khawla Bouafia", "0000-0001-7653-2730"),
    ("Ali Deran", "0000-0001-5377-6740"),
    ("Yosi KELLER", "0000-0002-2876-2790"),
    ("Matthias Fengler", "0000-0002-9862-9258"),
    ("Wolfgang Härdle", "0000-0001-5600-3014"),
    ("Ioannis Emiris", "0000-0002-2339-5303"),
    ("Nikolaos S. Thomaidis", "0000-0002-6796-6171"),
    ("Karsten Wenzlaff", "0000-0002-3670-9703"),
    ("Giovanni Lagioia", "0000-0002-7044-602X"),
    ("Christian Suter", "0000-0003-1477-3488"),
    ("Maria Elena De Giuli", "0000-0002-5221-0005"),
    ("Luisa Anderloni", "0000-0003-3159-5943"),
    ("Eda Orhun", "0000-0001-7153-4892"),
    ("Paola Vicard", "0000-0002-4103-7868"),
    ("Sabrina Giordano", "0000-0002-3635-9440"),
    ("Silvija Vlah Jeric", "0000-0003-4738-6337"),
    ("Juliana Imeraj", "0009-0006-5284-1460"),
    ("Erika Mináriková", "0000-0002-4230-2109"),
]

def normalize_name(name):
    if pd.isna(name): return ""
    normalized = str(name).lower().strip()
    for old, new in {'ć':'c','č':'c','š':'s','ş':'s','ž':'z','đ':'d','ń':'n','ł':'l','ö':'o','ü':'u','ä':'a','á':'a','é':'e','í':'i','ő':'o','ű':'u','ř':'r','ý':'y','ß':'ss','-':' ','.':''}.items():
        normalized = normalized.replace(old, new)
    return normalized

def find_member_row(df, target_name):
    target_normalized = normalize_name(target_name)
    target_parts = set(target_normalized.split())
    for idx, row in df.iterrows():
        fn = str(row.get('First Name', '')).strip() if pd.notna(row.get('First Name')) else ''
        ln = str(row.get('Last Name', '')).strip() if pd.notna(row.get('Last Name')) else ''
        row_normalized = normalize_name(f"{fn} {ln}")
        row_parts = set(row_normalized.split())
        if row_normalized == target_normalized: return idx
        if len(target_parts & row_parts) >= 2: return idx
    return None

def main():
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    excel_path = project_dir / 'working_groups_members' / 'CA19130-WG-members.xlsx'

    print(f"Reading: {excel_path}")
    df = pd.read_excel(excel_path)
    has_orcid = df['Orcid'].notna() & (df['Orcid'] != '')
    print(f"Members with ORCID before: {has_orcid.sum()}")

    added = 0
    for name, orcid in ORCIDS_TO_ADD:
        idx = find_member_row(df, name)
        if idx is not None:
            current = df.at[idx, 'Orcid']
            if pd.isna(current) or str(current).strip() == '':
                df.at[idx, 'Orcid'] = orcid
                print(f"  [ADDED] {name} -> {orcid}")
                added += 1

    df.to_excel(excel_path, index=False)
    has_orcid_new = df['Orcid'].notna() & (df['Orcid'] != '')
    print(f"Members with ORCID after: {has_orcid_new.sum()} (+{added})")
    return True

if __name__ == '__main__':
    main()
