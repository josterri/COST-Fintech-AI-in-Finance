"""
Apply Phase 1B: Visual fixes based on screenshot analysis.
Targets remaining whitespace issues found in visual review.
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).parent

# Phase 1B: Visual fixes CSS
PHASE1B_CSS = """
        /* === Phase 1B: Visual Fixes === */
        /* Ultra-minimal hero (1rem -> 0.5rem) */
        .hero { padding: 0.5rem 0 !important; }
        .hero h1 { font-size: 1.5rem !important; line-height: 1.2 !important; }
        .hero .subtitle { font-size: 0.9rem !important; margin-top: 0.15rem !important; }
        .hero .action-id { font-size: 0.75rem !important; padding: 0.15rem 0.5rem !important; }

        /* Tighter line-height globally */
        body { line-height: 1.4 !important; }

        /* Section margins reduced */
        section, .content-section { margin-bottom: 1rem !important; }
        .section-header { margin-bottom: 0.5rem !important; }

        /* Stats grid gap fix */
        .stats-grid, .impact-grid, .features-grid {
            gap: 1rem !important;
        }

        /* Card padding tighter */
        .card, .feature-card, .impact-card {
            padding: 0.75rem !important;
        }
        .card h3 { margin-bottom: 0.35rem !important; }
        .card p { margin-bottom: 0.25rem !important; }

        /* Explore cards more compact */
        .explore-card, .nav-card {
            padding: 0.75rem !important;
        }
        .explore-card h3 { font-size: 1rem !important; margin-bottom: 0.25rem !important; }
        .explore-card p { font-size: 0.8rem !important; }

        /* Working group cards tighter */
        .wg-card { padding: 0.75rem !important; }
        .wg-card h4 { font-size: 0.95rem !important; margin-bottom: 0.25rem !important; }

        /* Timeline more compact */
        .timeline-item { margin-bottom: 0.5rem !important; }
        .timeline-content { padding: 0.5rem 0.75rem !important; }

        /* Objective cards tighter */
        .objective-card { padding: 0.5rem !important; }
        .objective-card h4 { font-size: 0.85rem !important; }

        /* Achievement list compact */
        .achievement-item { padding: 0.35rem 0 !important; }

        /* Country pills tighter */
        .country-pill { padding: 0.2rem 0.5rem !important; font-size: 0.7rem !important; }

        /* Footer more compact */
        footer { padding: 1rem 0 !important; }

        /* Remove decorative elements that waste space */
        h2::after { height: 2px !important; margin-top: 0.25rem !important; }
        /* === End Phase 1B === */
"""

def add_phase1b_styles(content):
    """Add Phase 1B styles before closing </style> tag."""
    if '/* === Phase 1B: Visual Fixes ===' in content:
        print("    [SKIP] Already has Phase 1B styles")
        return content, False

    pattern = r'(</style>)'
    matches = list(re.finditer(pattern, content))

    if not matches:
        print("    [WARN] No </style> tag found")
        return content, False

    first_match = matches[0]
    insert_pos = first_match.start()

    new_content = content[:insert_pos] + PHASE1B_CSS + content[insert_pos:]
    return new_content, True

def process_file(filepath):
    """Process a single HTML file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        if 'sl-sidebar' not in content and 'hero' not in content:
            return False

        new_content, changed = add_phase1b_styles(content)

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

    print("Applying Phase 1B: Visual Fixes (based on screenshot analysis)")
    print("=" * 60)
    print("Changes: ultra-minimal hero, tighter line-height, reduced")
    print("         section margins, compact cards, timeline fixes")
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
    print("Total compaction now: ~45-55% (Option B + Phase 1 + Phase 1B)")

if __name__ == '__main__':
    main()
