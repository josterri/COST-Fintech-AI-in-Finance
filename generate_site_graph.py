"""
Generate a network graph visualization of the COST CA19130 site structure.
Shows how pages are linked through the navigation hierarchy.
"""

import json
import math
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx

# COST branding colors
COLORS = {
    'home': '#5B2D8A',      # Purple
    'category': '#2B5F9E',   # Blue
    'landing': '#E87722',    # Orange
    'page': '#00A0B0',       # Teal
    'subdir': '#7AB800',     # Green
    'edge': '#94a3b8',       # Gray
    'edge_light': '#cbd5e1'  # Light gray
}

def load_sitemap():
    """Load sitemap data from JSON."""
    sitemap_path = Path(__file__).parent / 'data' / 'sitemap.json'
    with open(sitemap_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def build_graph(sitemap):
    """Build a networkx graph from sitemap data."""
    G = nx.DiGraph()

    # Add HOME node
    G.add_node('HOME', type='home', label='HOME', size=2000)

    # Category landing pages
    landing_pages = {
        'IMPACT': 'impact.html',
        'NETWORK': 'network.html',
        'RESEARCH': 'research.html',
        'ACTIVITIES': 'activities.html',
        'ARCHIVE': 'archive.html'
    }

    # Add categories and their pages
    for category, pages in sitemap['categories'].items():
        if category == 'HOME':
            continue
        if category == 'OTHER':
            continue

        # Add category node
        G.add_node(category, type='category', label=category, size=1500)
        G.add_edge('HOME', category, weight=2)

        # Add page nodes
        for page in pages:
            page_name = page['name']
            title = page['title']

            # Determine if it's a landing page
            is_landing = page_name == landing_pages.get(category)
            node_type = 'landing' if is_landing else 'page'

            # Shorten title for display
            short_title = title[:20] + '...' if len(title) > 20 else title

            G.add_node(page_name, type=node_type, label=short_title,
                      size=800 if is_landing else 400, category=category)
            G.add_edge(category, page_name, weight=1)

    # Add subdirectories
    subdirs = sitemap['subdirectories']

    # Financial Reports -> ACTIVITIES
    if 'financial-reports' in subdirs:
        fr = subdirs['financial-reports']
        G.add_node('FINANCIAL', type='subdir', label=f"Financial\n({fr['count']})", size=1000)
        G.add_edge('ACTIVITIES', 'FINANCIAL', weight=1.5)

        # Add a few representative pages (not all 13)
        for page in fr['pages'][:3]:
            short = page['title'][:15]
            G.add_node(page['path'], type='page', label=short, size=300, category='FINANCIAL')
            G.add_edge('FINANCIAL', page['path'], weight=0.5)

    # Work Budget Plans -> ACTIVITIES
    if 'work-budget-plans' in subdirs:
        wbp = subdirs['work-budget-plans']
        G.add_node('BUDGET', type='subdir', label=f"Budget Plans\n({wbp['count']})", size=1000)
        G.add_edge('ACTIVITIES', 'BUDGET', weight=1.5)

        for page in wbp['pages'][:3]:
            short = page['title'][:15]
            G.add_node(page['path'], type='page', label=short, size=300, category='BUDGET')
            G.add_edge('BUDGET', page['path'], weight=0.5)

    # Action Chair Archive -> ARCHIVE
    if 'action-chair' in subdirs:
        ac = subdirs['action-chair']
        G.add_node('ACTION_CHAIR', type='subdir', label=f"Action Chair\nArchive ({ac['count']})", size=1200)
        G.add_edge('ARCHIVE', 'ACTION_CHAIR', weight=1.5)

        # Add folder nodes (simplified)
        for folder in ac['folders'][:4]:
            folder_name = folder['name'][:15]
            node_id = f"ac_{folder['name'][:10]}"
            G.add_node(node_id, type='page', label=folder_name, size=350, category='ACTION_CHAIR')
            G.add_edge('ACTION_CHAIR', node_id, weight=0.5)

    # Data Files node
    if sitemap.get('data_files'):
        count = len(sitemap['data_files'])
        G.add_node('DATA_FILES', type='subdir', label=f"Data Files\n({count})", size=900)
        G.add_edge('ARCHIVE', 'DATA_FILES', weight=1)

    return G

def calculate_positions(G):
    """Calculate node positions using a custom radial layout."""
    pos = {}

    # Center HOME
    pos['HOME'] = (0, 0)

    # Categories in a circle around HOME
    categories = ['IMPACT', 'NETWORK', 'RESEARCH', 'ACTIVITIES', 'ARCHIVE']
    cat_radius = 3
    for i, cat in enumerate(categories):
        if cat in G.nodes:
            angle = 2 * math.pi * i / len(categories) - math.pi/2
            pos[cat] = (cat_radius * math.cos(angle), cat_radius * math.sin(angle))

    # Position pages around their categories
    for cat in categories:
        if cat not in G.nodes:
            continue

        # Get pages connected to this category
        pages = [n for n in G.successors(cat) if G.nodes[n].get('type') in ['landing', 'page', 'subdir']]

        if not pages:
            continue

        cat_pos = pos[cat]
        page_radius = 1.8

        # Calculate angle offset to spread pages away from center
        center_angle = math.atan2(cat_pos[1], cat_pos[0])

        for j, page in enumerate(pages):
            # Spread pages in an arc around the category
            arc_span = math.pi * 0.8  # 144 degrees
            page_angle = center_angle - arc_span/2 + (j + 0.5) * arc_span / len(pages)

            px = cat_pos[0] + page_radius * math.cos(page_angle)
            py = cat_pos[1] + page_radius * math.sin(page_angle)
            pos[page] = (px, py)

            # Position sub-pages of subdirectories
            if G.nodes[page].get('type') == 'subdir':
                subpages = [n for n in G.successors(page)]
                sub_radius = 1.2
                for k, subpage in enumerate(subpages):
                    sub_arc = math.pi * 0.5
                    sub_angle = page_angle - sub_arc/2 + (k + 0.5) * sub_arc / max(len(subpages), 1)
                    sx = pos[page][0] + sub_radius * math.cos(sub_angle)
                    sy = pos[page][1] + sub_radius * math.sin(sub_angle)
                    pos[subpage] = (sx, sy)

    return pos

def draw_graph(G, pos):
    """Draw the network graph with custom styling."""
    plt.rcParams.update({
        'font.size': 9,
        'font.family': 'sans-serif',
        'figure.facecolor': 'white'
    })

    fig, ax = plt.subplots(figsize=(14, 10), dpi=150)
    ax.set_facecolor('#f8fafc')

    # Draw edges first (behind nodes)
    for u, v, data in G.edges(data=True):
        x = [pos[u][0], pos[v][0]]
        y = [pos[u][1], pos[v][1]]
        weight = data.get('weight', 1)
        alpha = 0.6 if weight > 1 else 0.3
        width = 2 if weight > 1 else 1
        ax.plot(x, y, color=COLORS['edge'], linewidth=width, alpha=alpha, zorder=1)

    # Draw nodes by type
    for node_type, color in [('home', COLORS['home']),
                              ('category', COLORS['category']),
                              ('subdir', COLORS['subdir']),
                              ('landing', COLORS['landing']),
                              ('page', COLORS['page'])]:
        nodes = [n for n in G.nodes if G.nodes[n].get('type') == node_type]
        if not nodes:
            continue

        sizes = [G.nodes[n].get('size', 400) for n in nodes]
        x = [pos[n][0] for n in nodes]
        y = [pos[n][1] for n in nodes]

        ax.scatter(x, y, s=sizes, c=color, alpha=0.9, zorder=2, edgecolors='white', linewidths=2)

        # Add labels
        for n in nodes:
            label = G.nodes[n].get('label', n)
            fontsize = 10 if node_type in ['home', 'category'] else 7 if node_type == 'subdir' else 6
            fontweight = 'bold' if node_type in ['home', 'category', 'subdir'] else 'normal'

            # Offset label slightly
            offset_y = 0.3 if G.nodes[n].get('size', 400) > 800 else 0.2
            ax.annotate(label, (pos[n][0], pos[n][1] - offset_y),
                       ha='center', va='top', fontsize=fontsize, fontweight=fontweight,
                       color='#1e293b', zorder=3)

    # Add title
    ax.set_title('COST CA19130 Site Structure\n217 Pages Across 5 Categories',
                fontsize=14, fontweight='bold', color=COLORS['home'], pad=20)

    # Add legend
    legend_elements = [
        mpatches.Patch(color=COLORS['home'], label='Home'),
        mpatches.Patch(color=COLORS['category'], label='Categories (5)'),
        mpatches.Patch(color=COLORS['landing'], label='Landing Pages'),
        mpatches.Patch(color=COLORS['page'], label='Content Pages'),
        mpatches.Patch(color=COLORS['subdir'], label='Subdirectories'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=8, framealpha=0.9)

    # Clean up axes
    ax.set_xlim(-8, 8)
    ax.set_ylim(-7, 7)
    ax.axis('off')

    plt.tight_layout()
    return fig

def main():
    print("Loading sitemap data...")
    sitemap = load_sitemap()

    print(f"Building graph from {sitemap['statistics']['total_pages']} pages...")
    G = build_graph(sitemap)
    print(f"  Nodes: {G.number_of_nodes()}")
    print(f"  Edges: {G.number_of_edges()}")

    print("Calculating layout...")
    pos = calculate_positions(G)

    print("Rendering graph...")
    fig = draw_graph(G, pos)

    # Save output
    output_path = Path(__file__).parent / 'site_graph.png'
    fig.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"Saved: {output_path}")

    plt.close()
    print("Done!")

if __name__ == '__main__':
    main()
