"""
Add About link to sidebar navigation in all HTML files.
"""

import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent

# Directories to process
DIRECTORIES = [
    BASE_DIR,
    BASE_DIR / "financial-reports",
    BASE_DIR / "work-budget-plans",
]

def add_about_link(content, prefix=""):
    """Add About link to sidebar after Site Map link."""
    # Check if About link already exists
    if 'href="' + prefix + 'about.html"' in content:
        return content, False

    # Pattern to find Site Map link in sidebar
    pattern = r'(<a href="' + re.escape(prefix) + r'sitemap\.html">Site Map</a>)'
    match = re.search(pattern, content)

    if not match:
        return content, False

    # Insert About link after Site Map
    about_link = f'\n                <a href="{prefix}about.html">About</a>'
    insert_pos = match.end()
    new_content = content[:insert_pos] + about_link + content[insert_pos:]

    return new_content, True

def process_file(file_path, prefix=""):
    """Process a single HTML file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"  Error reading {file_path}: {e}")
        return False

    # Skip if no sidebar
    if 'sl-sidebar' not in content:
        return False

    original_content = content
    content, added = add_about_link(content, prefix)

    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True

    return False

def main():
    print("Adding About link to sidebar navigation...")
    print("=" * 60)

    total_files = 0
    modified_files = 0

    # Root directory files (no prefix)
    for file in BASE_DIR.glob("*.html"):
        if '_backup' in str(file) or 'test-' in file.name:
            continue
        total_files += 1
        if process_file(file, prefix=""):
            modified_files += 1
            print(f"  Updated: {file.name}")

    # Subdirectory files (with ../ prefix)
    for subdir in ["financial-reports", "work-budget-plans"]:
        subdir_path = BASE_DIR / subdir
        if not subdir_path.exists():
            continue
        for file in subdir_path.glob("*.html"):
            total_files += 1
            if process_file(file, prefix="../"):
                modified_files += 1
                rel_path = file.relative_to(BASE_DIR)
                print(f"  Updated: {rel_path}")

    print("=" * 60)
    print(f"Summary:")
    print(f"  Total HTML files scanned: {total_files}")
    print(f"  Files modified: {modified_files}")

if __name__ == "__main__":
    main()
