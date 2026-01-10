"""
Fix relative navigation links in Action Chair subdirectory HTML files.
These pages have href="index.html" etc. that should point to root-level pages.
"""

import os
import re
import sys
import io
from pathlib import Path

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_DIR = Path(__file__).parent
ACTION_CHAIR_DIR = BASE_DIR / "Action Chair"

# Navigation links that should point to root
ROOT_PAGES = ['index.html', 'documents.html', 'midterm-report.html']

def get_relative_prefix(file_path):
    """Calculate the relative path prefix needed to reach root from this file."""
    rel_path = file_path.relative_to(BASE_DIR)
    depth = len(rel_path.parts) - 1  # -1 because the file itself doesn't count
    if depth == 0:
        return ""
    return "../" * depth

def fix_html_file(file_path):
    """Fix navigation links in a single HTML file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"  Error reading {file_path}: {e}")
        return 0

    original_content = content
    prefix = get_relative_prefix(file_path)
    fixes = 0

    for page in ROOT_PAGES:
        # Pattern matches href="page.html" without any path prefix
        pattern = rf'href="({re.escape(page)})"'
        if re.search(pattern, content):
            replacement = f'href="{prefix}{page}"'
            count = len(re.findall(pattern, content))
            content = re.sub(pattern, replacement, content)
            fixes += count

    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return fixes

    return 0

def main():
    print("Scanning Action Chair directory for HTML files...")

    total_files = 0
    total_fixes = 0
    fixed_files = 0

    for root, dirs, files in os.walk(ACTION_CHAIR_DIR):
        for file in files:
            if file.endswith('.html'):
                file_path = Path(root) / file
                total_files += 1

                fixes = fix_html_file(file_path)
                if fixes > 0:
                    fixed_files += 1
                    total_fixes += fixes
                    rel_path = file_path.relative_to(BASE_DIR)
                    print(f"  Fixed {fixes} links in: {rel_path}")

    print(f"\nSummary:")
    print(f"  Files scanned: {total_files}")
    print(f"  Files fixed: {fixed_files}")
    print(f"  Total links fixed: {total_fixes}")

if __name__ == "__main__":
    main()
