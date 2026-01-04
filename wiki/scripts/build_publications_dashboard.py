"""
COST Action CA19130 Wiki - Publications Dashboard Builder

Creates the interactive publications dashboard with:
- Statistics overview
- Year and type distribution charts
- Search and filter functionality
- Paginated results list
"""

import json
from pathlib import Path
from collections import defaultdict, Counter

# Paths
REPO_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = REPO_ROOT / "data"
DOCS_DIR = Path(__file__).parent.parent / "docs"
DATA_OUTPUT_DIR = DOCS_DIR / "data"

def load_publications():
    """Load publications from ORCID data."""
    filepath = DATA_DIR / "orcid_publications.json"
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def prepare_publications_json(data):
    """Prepare a simplified publications JSON for the dashboard."""
    publications = data.get('publications', [])

    # Create simplified list for frontend
    pub_list = []
    for pub in publications:
        pub_list.append({
            'id': pub.get('orcid_put_code', ''),
            'title': pub.get('title', 'Untitled'),
            'year': pub.get('year', 0),
            'type': pub.get('type', 'other'),
            'venue': pub.get('venue', ''),
            'doi': pub.get('doi', ''),
            'author': pub.get('cost_author', {}).get('name', 'Unknown'),
            'author_orcid': pub.get('cost_author', {}).get('orcid', ''),
            'apa': pub.get('apa_citation', '')
        })

    # Sort by year descending, then title
    pub_list.sort(key=lambda x: (-x['year'], x['title'].lower()))

    return pub_list

def compute_statistics(publications):
    """Compute statistics for the dashboard."""
    years = Counter(p['year'] for p in publications if p['year'])
    types = Counter(p['type'] for p in publications if p['type'])
    authors = set(p['author'] for p in publications if p['author'])
    with_doi = sum(1 for p in publications if p['doi'])

    return {
        'total': len(publications),
        'with_doi': with_doi,
        'unique_authors': len(authors),
        'years': dict(sorted(years.items())),
        'types': dict(types)
    }

def generate_dashboard_html():
    """Generate the publications dashboard markdown with embedded JavaScript."""
    return '''# Publications Explorer

<div class="dashboard-stats" id="stats-container">
<div class="stat-card">
<span class="stat-value" id="stat-total">-</span>
<span class="stat-label">Publications</span>
</div>
<div class="stat-card">
<span class="stat-value" id="stat-authors">-</span>
<span class="stat-label">Authors</span>
</div>
<div class="stat-card">
<span class="stat-value" id="stat-doi">-</span>
<span class="stat-label">With DOI</span>
</div>
<div class="stat-card">
<span class="stat-value" id="stat-filtered">-</span>
<span class="stat-label">Showing</span>
</div>
</div>

## Distribution

<div class="charts-row">
<div class="chart-card">
<h3>Publications by Year</h3>
<canvas id="yearChart" height="200"></canvas>
</div>
<div class="chart-card">
<h3>Publications by Type</h3>
<canvas id="typeChart" height="200"></canvas>
</div>
</div>

## Search & Filter

<div class="filter-controls">
<div class="filter-row">
<input type="text" id="searchInput" placeholder="Search titles, authors, venues..." class="search-input">
<select id="yearFilter" class="filter-select">
<option value="">All Years</option>
</select>
<select id="typeFilter" class="filter-select">
<option value="">All Types</option>
</select>
<select id="authorFilter" class="filter-select">
<option value="">All Authors</option>
</select>
<button onclick="clearFilters()" class="clear-btn">Clear</button>
</div>
<div class="export-row">
<button onclick="exportCSV()" class="export-btn">Export CSV</button>
<button onclick="exportBibTeX()" class="export-btn">Export BibTeX</button>
</div>
</div>

## Results

<div id="results-container">
<div class="loading">Loading publications...</div>
</div>

<div id="pagination-container"></div>

<script>
// Publications Dashboard JavaScript
let allPublications = [];
let filteredPublications = [];
let currentPage = 1;
const perPage = 25;

// Type labels
const typeLabels = {
    'journal-article': 'Journal Article',
    'conference-paper': 'Conference Paper',
    'book-chapter': 'Book Chapter',
    'book': 'Book',
    'preprint': 'Preprint',
    'other': 'Other'
};

// Initialize
document.addEventListener('DOMContentLoaded', async function() {
    await loadPublications();
    setupEventListeners();
    applyFiltersFromURL();
});

async function loadPublications() {
    try {
        const response = await fetch('../data/publications_dashboard.json');
        if (!response.ok) throw new Error('Failed to load');
        const data = await response.json();
        allPublications = data.publications;

        // Update stats
        document.getElementById('stat-total').textContent = data.stats.total.toLocaleString();
        document.getElementById('stat-authors').textContent = data.stats.unique_authors.toLocaleString();
        document.getElementById('stat-doi').textContent = data.stats.with_doi.toLocaleString();

        // Populate filters
        populateFilters(data.stats);

        // Create charts
        createCharts(data.stats);

        // Initial render
        applyFilters();
    } catch (e) {
        document.getElementById('results-container').innerHTML =
            '<div class="error">Failed to load publications. Please refresh the page.</div>';
        console.error(e);
    }
}

function populateFilters(stats) {
    // Years
    const yearSelect = document.getElementById('yearFilter');
    const years = Object.keys(stats.years).sort((a,b) => b-a);
    years.forEach(year => {
        const opt = document.createElement('option');
        opt.value = year;
        opt.textContent = `${year} (${stats.years[year]})`;
        yearSelect.appendChild(opt);
    });

    // Types
    const typeSelect = document.getElementById('typeFilter');
    Object.entries(stats.types).sort((a,b) => b[1]-a[1]).forEach(([type, count]) => {
        const opt = document.createElement('option');
        opt.value = type;
        opt.textContent = `${typeLabels[type] || type} (${count})`;
        typeSelect.appendChild(opt);
    });

    // Authors - get unique sorted
    const authors = [...new Set(allPublications.map(p => p.author))].sort();
    const authorSelect = document.getElementById('authorFilter');
    authors.forEach(author => {
        const opt = document.createElement('option');
        opt.value = author;
        opt.textContent = author;
        authorSelect.appendChild(opt);
    });
}

function createCharts(stats) {
    // Year chart
    const yearCtx = document.getElementById('yearChart');
    if (yearCtx && typeof Chart !== 'undefined') {
        const years = Object.keys(stats.years).sort();
        const yearCounts = years.map(y => stats.years[y]);

        new Chart(yearCtx, {
            type: 'bar',
            data: {
                labels: years,
                datasets: [{
                    label: 'Publications',
                    data: yearCounts,
                    backgroundColor: '#5B2D8A',
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: { y: { beginAtZero: true } }
            }
        });
    }

    // Type chart
    const typeCtx = document.getElementById('typeChart');
    if (typeCtx && typeof Chart !== 'undefined') {
        const types = Object.keys(stats.types);
        const typeCounts = types.map(t => stats.types[t]);
        const typeColors = ['#5B2D8A', '#2B5F9E', '#00A0B0', '#E87722', '#7AB800', '#D62728'];

        new Chart(typeCtx, {
            type: 'doughnut',
            data: {
                labels: types.map(t => typeLabels[t] || t),
                datasets: [{
                    data: typeCounts,
                    backgroundColor: typeColors
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        });
    }
}

function setupEventListeners() {
    document.getElementById('searchInput').addEventListener('input', debounce(applyFilters, 300));
    document.getElementById('yearFilter').addEventListener('change', applyFilters);
    document.getElementById('typeFilter').addEventListener('change', applyFilters);
    document.getElementById('authorFilter').addEventListener('change', applyFilters);
}

function applyFilters() {
    const search = document.getElementById('searchInput').value.toLowerCase();
    const year = document.getElementById('yearFilter').value;
    const type = document.getElementById('typeFilter').value;
    const author = document.getElementById('authorFilter').value;

    filteredPublications = allPublications.filter(pub => {
        if (year && pub.year != year) return false;
        if (type && pub.type !== type) return false;
        if (author && pub.author !== author) return false;
        if (search) {
            const text = `${pub.title} ${pub.author} ${pub.venue}`.toLowerCase();
            if (!text.includes(search)) return false;
        }
        return true;
    });

    currentPage = 1;
    updateURL();
    renderResults();
}

function renderResults() {
    const container = document.getElementById('results-container');
    document.getElementById('stat-filtered').textContent = filteredPublications.length.toLocaleString();

    if (filteredPublications.length === 0) {
        container.innerHTML = '<div class="no-results">No publications match your filters.</div>';
        document.getElementById('pagination-container').innerHTML = '';
        return;
    }

    // Paginate
    const start = (currentPage - 1) * perPage;
    const end = start + perPage;
    const pageData = filteredPublications.slice(start, end);

    // Render
    let html = '<div class="publication-list">';
    pageData.forEach(pub => {
        const typeClass = pub.type.replace(/[^a-z]/g, '-');
        html += `
        <div class="publication-item">
            <div class="pub-header">
                <span class="pub-type pub-type-${typeClass}">${typeLabels[pub.type] || pub.type}</span>
                <span class="pub-year">${pub.year}</span>
            </div>
            <h4 class="pub-title">${escapeHtml(pub.title)}</h4>
            <div class="pub-author">${escapeHtml(pub.author)}</div>
            ${pub.venue ? `<div class="pub-venue">${escapeHtml(pub.venue)}</div>` : ''}
            ${pub.doi ? `<a href="${pub.doi}" target="_blank" class="pub-doi">DOI</a>` : ''}
        </div>`;
    });
    html += '</div>';
    container.innerHTML = html;

    // Pagination
    renderPagination();
}

function renderPagination() {
    const container = document.getElementById('pagination-container');
    const totalPages = Math.ceil(filteredPublications.length / perPage);

    if (totalPages <= 1) {
        container.innerHTML = '';
        return;
    }

    let html = '<div class="pagination">';
    html += `<button onclick="goToPage(${currentPage - 1})" ${currentPage === 1 ? 'disabled' : ''}>Prev</button>`;

    // Page numbers
    const pages = getPageNumbers(totalPages);
    pages.forEach(p => {
        if (p === '...') {
            html += '<span class="pagination-ellipsis">...</span>';
        } else {
            html += `<button onclick="goToPage(${p})" class="${p === currentPage ? 'active' : ''}">${p}</button>`;
        }
    });

    html += `<button onclick="goToPage(${currentPage + 1})" ${currentPage === totalPages ? 'disabled' : ''}>Next</button>`;
    html += '</div>';
    container.innerHTML = html;
}

function getPageNumbers(total) {
    const current = currentPage;
    const pages = [];

    if (total <= 7) {
        for (let i = 1; i <= total; i++) pages.push(i);
    } else {
        pages.push(1);
        if (current > 3) pages.push('...');
        for (let i = Math.max(2, current - 1); i <= Math.min(total - 1, current + 1); i++) {
            pages.push(i);
        }
        if (current < total - 2) pages.push('...');
        pages.push(total);
    }
    return pages;
}

function goToPage(page) {
    const totalPages = Math.ceil(filteredPublications.length / perPage);
    currentPage = Math.max(1, Math.min(page, totalPages));
    renderResults();
    window.scrollTo({ top: document.getElementById('results-container').offsetTop - 100, behavior: 'smooth' });
}

function clearFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('yearFilter').value = '';
    document.getElementById('typeFilter').value = '';
    document.getElementById('authorFilter').value = '';
    applyFilters();
}

function updateURL() {
    const params = new URLSearchParams();
    const search = document.getElementById('searchInput').value;
    const year = document.getElementById('yearFilter').value;
    const type = document.getElementById('typeFilter').value;
    const author = document.getElementById('authorFilter').value;

    if (search) params.set('q', search);
    if (year) params.set('year', year);
    if (type) params.set('type', type);
    if (author) params.set('author', author);

    const newURL = params.toString() ? `?${params}` : window.location.pathname;
    history.replaceState(null, '', newURL);
}

function applyFiltersFromURL() {
    const params = new URLSearchParams(window.location.search);

    if (params.get('q')) document.getElementById('searchInput').value = params.get('q');
    if (params.get('year')) document.getElementById('yearFilter').value = params.get('year');
    if (params.get('type')) document.getElementById('typeFilter').value = params.get('type');
    if (params.get('author')) document.getElementById('authorFilter').value = params.get('author');

    if (params.toString()) applyFilters();
}

function exportCSV() {
    const headers = ['Title', 'Author', 'Year', 'Type', 'Venue', 'DOI'];
    const rows = filteredPublications.map(p => [
        `"${(p.title || '').replace(/"/g, '""')}"`,
        `"${(p.author || '').replace(/"/g, '""')}"`,
        p.year,
        p.type,
        `"${(p.venue || '').replace(/"/g, '""')}"`,
        p.doi || ''
    ]);

    const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\\n');
    downloadFile(csv, 'publications.csv', 'text/csv');
}

function exportBibTeX() {
    let bibtex = '';
    filteredPublications.forEach((p, i) => {
        const key = `pub${i + 1}`;
        const type = p.type === 'journal-article' ? 'article' :
                     p.type === 'conference-paper' ? 'inproceedings' :
                     p.type === 'book-chapter' ? 'incollection' : 'misc';

        bibtex += `@${type}{${key},\\n`;
        bibtex += `  title = {${p.title}},\\n`;
        bibtex += `  author = {${p.author}},\\n`;
        bibtex += `  year = {${p.year}},\\n`;
        if (p.venue) bibtex += `  journal = {${p.venue}},\\n`;
        if (p.doi) bibtex += `  doi = {${p.doi.replace('https://doi.org/', '')}},\\n`;
        bibtex += `}\\n\\n`;
    });

    downloadFile(bibtex, 'publications.bib', 'text/plain');
}

function downloadFile(content, filename, type) {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
</script>

<style>
.dashboard-stats {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 2rem;
}
.stat-card {
    background: var(--md-code-bg-color);
    padding: 1.5rem;
    border-radius: 8px;
    text-align: center;
}
.stat-value {
    display: block;
    font-size: 2rem;
    font-weight: 700;
    color: var(--md-primary-fg-color);
}
.stat-label {
    font-size: 0.9rem;
    color: var(--md-default-fg-color--light);
}
.charts-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
    margin-bottom: 2rem;
}
.chart-card {
    background: var(--md-code-bg-color);
    padding: 1.5rem;
    border-radius: 8px;
}
.chart-card h3 {
    margin-top: 0;
    font-size: 1rem;
}
.filter-controls {
    background: var(--md-code-bg-color);
    padding: 1.5rem;
    border-radius: 8px;
    margin-bottom: 2rem;
}
.filter-row {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
    margin-bottom: 1rem;
}
.search-input {
    flex: 2;
    min-width: 200px;
    padding: 0.5rem 1rem;
    border: 1px solid var(--md-default-fg-color--lightest);
    border-radius: 4px;
    font-size: 0.95rem;
}
.filter-select {
    flex: 1;
    min-width: 120px;
    padding: 0.5rem;
    border: 1px solid var(--md-default-fg-color--lightest);
    border-radius: 4px;
}
.clear-btn, .export-btn {
    padding: 0.5rem 1rem;
    background: var(--md-primary-fg-color);
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}
.clear-btn:hover, .export-btn:hover {
    opacity: 0.9;
}
.export-row {
    display: flex;
    gap: 0.5rem;
}
.publication-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}
.publication-item {
    background: var(--md-code-bg-color);
    padding: 1rem;
    border-radius: 8px;
    border-left: 3px solid var(--md-primary-fg-color);
}
.pub-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
}
.pub-type {
    font-size: 0.75rem;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    background: var(--md-primary-fg-color);
    color: white;
}
.pub-year {
    font-weight: 600;
    color: var(--md-default-fg-color--light);
}
.pub-title {
    margin: 0.5rem 0;
    font-size: 1rem;
}
.pub-author {
    color: var(--md-default-fg-color--light);
    font-size: 0.9rem;
}
.pub-venue {
    font-style: italic;
    font-size: 0.85rem;
    color: var(--md-default-fg-color--light);
}
.pub-doi {
    display: inline-block;
    margin-top: 0.5rem;
    font-size: 0.8rem;
    padding: 0.2rem 0.5rem;
    background: var(--md-accent-fg-color);
    color: white;
    border-radius: 4px;
    text-decoration: none;
}
.pagination {
    display: flex;
    justify-content: center;
    gap: 0.25rem;
    margin-top: 2rem;
}
.pagination button {
    padding: 0.5rem 0.75rem;
    border: 1px solid var(--md-default-fg-color--lightest);
    background: var(--md-code-bg-color);
    cursor: pointer;
    border-radius: 4px;
}
.pagination button.active {
    background: var(--md-primary-fg-color);
    color: white;
    border-color: var(--md-primary-fg-color);
}
.pagination button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}
.no-results, .loading, .error {
    text-align: center;
    padding: 2rem;
    color: var(--md-default-fg-color--light);
}
.error { color: #d62728; }

@media (max-width: 768px) {
    .dashboard-stats { grid-template-columns: repeat(2, 1fr); }
    .charts-row { grid-template-columns: 1fr; }
    .filter-row { flex-direction: column; }
    .search-input, .filter-select { min-width: 100%; }
}
</style>
'''


def main():
    """Main entry point."""
    print("Building Publications Dashboard...")

    # Load data
    data = load_publications()
    print(f"Loaded {data['metadata']['total_publications']} publications")

    # Prepare simplified JSON
    publications = prepare_publications_json(data)
    stats = compute_statistics(publications)

    # Create data output directory
    DATA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Write dashboard JSON
    dashboard_data = {
        'publications': publications,
        'stats': stats
    }

    output_path = DATA_OUTPUT_DIR / "publications_dashboard.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dashboard_data, f, ensure_ascii=False)
    print(f"Created {output_path}")

    # Generate dashboard page
    dashboard_md = generate_dashboard_html()

    # Write to publications index
    pubs_dir = DOCS_DIR / "research" / "publications"
    pubs_dir.mkdir(parents=True, exist_ok=True)

    dashboard_path = pubs_dir / "index.md"
    with open(dashboard_path, 'w', encoding='utf-8') as f:
        f.write(dashboard_md)
    print(f"Created {dashboard_path}")

    print(f"\nDashboard Statistics:")
    print(f"  Total publications: {stats['total']}")
    print(f"  Unique authors: {stats['unique_authors']}")
    print(f"  With DOI: {stats['with_doi']}")
    print(f"  Years: {min(stats['years'].keys())} - {max(stats['years'].keys())}")
    print(f"  Types: {', '.join(stats['types'].keys())}")

    print("\nDone!")


if __name__ == "__main__":
    main()
