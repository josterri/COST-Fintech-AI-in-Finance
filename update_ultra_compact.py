"""
Apply Ultra-Compact Mode with user-specified values.
Extreme density - 0.1rem gaps, 1.2 line-height, 0.8rem font.
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).parent

# Ultra-Compact CSS with user's exact values
ULTRA_COMPACT_CSS = """
        /* === ULTRA-COMPACT MODE === */
        /* Layout: 140px sidebar, 24px topbar */
        :root {
            --sl-sidebar-width: 140px !important;
            --sl-topbar-height: 24px !important;
        }
        .sl-sidebar { width: 140px !important; }
        .sl-main { margin-left: 140px !important; }
        .sl-topbar { height: 24px !important; }
        .sl-topbar-tab { padding: 0.2rem 0.4rem !important; font-size: 0.55rem !important; }

        /* Hero: 0.1rem padding */
        .hero { padding: 0.1rem 0 !important; }
        .hero h1 { margin-bottom: 0.1rem !important; font-size: 1.4rem !important; }
        .hero .subtitle { margin-top: 0 !important; }

        /* Typography: 0.8rem font, 1.2 line-height */
        body {
            font-size: 0.8rem !important;
            line-height: 1.2 !important;
        }

        /* Headings: 0.1rem margins */
        h2 { margin: 0.1rem 0 !important; font-size: 1.3rem !important; }
        h3 { margin: 0.1rem 0 !important; font-size: 1.1rem !important; }
        h4 { margin: 0.1rem 0 !important; font-size: 0.95rem !important; }

        /* Lists: zero spacing */
        ul, ol { margin: 0 !important; padding-left: 1rem !important; }
        li { margin-bottom: 0 !important; }

        /* Grids: 0.1rem gaps */
        .stats-grid, .features-grid, .sections-grid,
        .wg-grid, .charts-grid, .objectives-grid,
        .impact-grid, .countries-list, .filter-pills {
            gap: 0.1rem !important;
        }

        /* Cards: 0.1rem padding */
        .card, .feature-card, .impact-card,
        .wg-card, .objective-card, .explore-card,
        .nav-card, .stat-card, .section-card {
            padding: 0.1rem !important;
        }
        .card h3, .card h4 { margin-bottom: 0.1rem !important; }
        .card p { margin-bottom: 0.1rem !important; }

        /* Tables: 0.1rem padding */
        th, td { padding: 0.1rem !important; }
        table { font-size: 0.75rem !important; }

        /* Sections: 0.1rem margins */
        section, .content-section { margin-bottom: 0.1rem !important; padding: 0.1rem !important; }
        .section-header { margin-bottom: 0.1rem !important; }

        /* Charts: 100px height */
        .chart-wrapper { height: 100px !important; }
        .chart-container { padding: 0.1rem !important; }

        /* Stats banner ultra-tight */
        .stats-banner { padding: 0.1rem !important; gap: 0.1rem !important; }
        .stat-number { font-size: 1.2rem !important; }
        .stat-label { font-size: 0.6rem !important; }

        /* Timeline compact */
        .timeline-item { margin-bottom: 0.1rem !important; }
        .timeline-content { padding: 0.1rem !important; }

        /* Country pills tight */
        .country-pill { padding: 0.1rem 0.3rem !important; font-size: 0.6rem !important; }

        /* Sidebar links tight */
        .sl-links a { padding: 0.15rem 0.3rem !important; font-size: 0.6rem !important; }
        .sl-section-header { padding: 0.2rem 0.4rem !important; font-size: 0.55rem !important; }

        /* Footer minimal */
        footer { padding: 0.1rem 0 !important; }

        /* Remove decorative elements */
        h2::after { display: none !important; }

        /* Responsive */
        @media (min-width: 901px) {
            .sl-main { margin-left: 140px !important; }
        }
        /* === END ULTRA-COMPACT === */
"""

def add_ultra_compact_styles(content):
    """Add ultra-compact styles before closing </style> tag."""
    if '/* === ULTRA-COMPACT MODE ===' in content:
        print("    [SKIP] Already has ultra-compact styles")
        return content, False

    pattern = r'(</style>)'
    matches = list(re.finditer(pattern, content))

    if not matches:
        print("    [WARN] No </style> tag found")
        return content, False

    first_match = matches[0]
    insert_pos = first_match.start()

    new_content = content[:insert_pos] + ULTRA_COMPACT_CSS + content[insert_pos:]
    return new_content, True

def process_file(filepath):
    """Process a single HTML file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        if 'sl-sidebar' not in content and 'hero' not in content:
            return False

        new_content, changed = add_ultra_compact_styles(content)

        if changed:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
        return False
    except Exception as e:
        print(f"    [ERROR] {e}")
        return False

def main():
    updated_count = 0
    skipped_count = 0

    print("Applying ULTRA-COMPACT MODE")
    print("=" * 60)
    print("Settings: 0.1rem gaps, 1.2 line-height, 0.8rem font")
    print("          140px sidebar, 24px topbar, 100px charts")
    print("=" * 60)

    # Root HTML files
    print("\n[ROOT PAGES]")
    for f in sorted(BASE_DIR.glob('*.html')):
        if f.name.startswith('test-'):
            continue
        print(f"  {f.name}...", end='')
        if process_file(f):
            print(" [UPDATED]")
            updated_count += 1
        else:
            print(" [skipped]")
            skipped_count += 1

    # Financial reports
    subdir = BASE_DIR / 'financial-reports'
    if subdir.exists():
        print("\n[FINANCIAL REPORTS]")
        for f in sorted(subdir.glob('*.html')):
            print(f"  {f.name}...", end='')
            if process_file(f):
                print(" [UPDATED]")
                updated_count += 1
            else:
                print(" [skipped]")
                skipped_count += 1

    # Work budget plans
    subdir = BASE_DIR / 'work-budget-plans'
    if subdir.exists():
        print("\n[WORK BUDGET PLANS]")
        for f in sorted(subdir.glob('*.html')):
            print(f"  {f.name}...", end='')
            if process_file(f):
                print(" [UPDATED]")
                updated_count += 1
            else:
                print(" [skipped]")
                skipped_count += 1

    print("\n" + "=" * 60)
    print(f"SUMMARY: Updated {updated_count} files, skipped {skipped_count}")
    print("Total compaction: ~60-70% from original (ULTRA-COMPACT)")

if __name__ == '__main__':
    main()
