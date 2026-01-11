"""
Add COST acknowledgements, EU funding statement, and officer information to all HTML file footers.
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

# CSS for acknowledgement section
ACKNOWLEDGEMENT_CSS = """
        .legacy-footer-acknowledgement {
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
            padding: 1rem 1.5rem;
            margin: 1.5rem auto;
            max-width: 800px;
            text-align: center;
        }

        .legacy-footer-acknowledgement p {
            color: rgba(255,255,255,0.85);
            font-size: 0.85rem;
            margin-bottom: 0.5rem;
            line-height: 1.6;
        }

        .legacy-footer-acknowledgement p:last-child {
            margin-bottom: 0;
        }

        .legacy-footer-acknowledgement .officers {
            color: rgba(255,255,255,0.7);
            font-size: 0.8rem;
            margin-top: 0.75rem;
            padding-top: 0.75rem;
            border-top: 1px solid rgba(255,255,255,0.1);
        }
"""

# HTML for acknowledgement section
ACKNOWLEDGEMENT_HTML = """            <div class="legacy-footer-acknowledgement">
                <p>This archive is based upon work from COST Action CA19130 - Fintech and Artificial Intelligence in Finance, supported by COST (European Cooperation in Science and Technology).</p>
                <p>Funded by the Horizon 2020 Framework Programme of the European Union.</p>
                <p class="officers"><strong>Science Officer:</strong> Dr Ralph Stuebner | <strong>Administrative Officer:</strong> Ms Rose Cruz Santos</p>
            </div>
"""

def add_css_if_missing(content):
    """Add acknowledgement CSS if not already present."""
    if '.legacy-footer-acknowledgement' in content:
        return content, False

    # Find the </style> tag and insert CSS before it
    # Look for the last </style> tag
    style_end = content.rfind('</style>')
    if style_end == -1:
        return content, False

    # Insert CSS before </style>
    new_content = content[:style_end] + ACKNOWLEDGEMENT_CSS + "\n    " + content[style_end:]
    return new_content, True

def add_html_if_missing(content):
    """Add acknowledgement HTML to footer if not already present."""
    if 'legacy-footer-acknowledgement' in content and 'Science Officer' in content:
        return content, False

    # Find the legacy-footer-bottom div and insert before it
    pattern = r'(<div class="legacy-footer-bottom">)'
    match = re.search(pattern, content)

    if not match:
        return content, False

    # Insert acknowledgement HTML before legacy-footer-bottom
    insert_pos = match.start()
    new_content = content[:insert_pos] + ACKNOWLEDGEMENT_HTML + content[insert_pos:]
    return new_content, True

def process_file(file_path):
    """Process a single HTML file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"  Error reading {file_path}: {e}")
        return False

    # Skip if not a page with legacy-footer
    if 'legacy-footer' not in content:
        return False

    original_content = content
    css_added = False
    html_added = False

    # Add CSS
    content, css_added = add_css_if_missing(content)

    # Add HTML
    content, html_added = add_html_if_missing(content)

    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True

    return False

def main():
    print("Adding COST acknowledgements to all HTML files...")
    print("=" * 60)

    total_files = 0
    modified_files = 0

    for directory in DIRECTORIES:
        if not directory.exists():
            continue

        for file in directory.glob("*.html"):
            # Skip backup and test files
            if '_backup' in str(file) or 'test-' in file.name:
                continue

            total_files += 1

            if process_file(file):
                modified_files += 1
                rel_path = file.relative_to(BASE_DIR)
                print(f"  Updated: {rel_path}")

    print("=" * 60)
    print(f"Summary:")
    print(f"  Total HTML files scanned: {total_files}")
    print(f"  Files modified: {modified_files}")
    print(f"  Files already up-to-date: {total_files - modified_files}")

if __name__ == "__main__":
    main()
