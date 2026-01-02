"""
Generate comprehensive HTML pages with tabbed interface from JSON data.
Creates: final-action-chair-report-full.html, midterm-action-chair-report-full.html, comparison-action-chair-full.html
"""

import json
from pathlib import Path
from datetime import datetime


# COST Action branding colors
CSS_STYLES = """
<style>
    :root {
        --cost-purple: #5B2D8A;
        --cost-purple-light: #7B4DAA;
        --cost-blue: #2B5F9E;
        --cost-blue-light: #4B7FBE;
        --cost-orange: #E87722;
        --cost-green: #28a745;
        --cost-red: #dc3545;
        --cost-gray: #6c757d;
        --bg-light: #f8f9fa;
        --border-color: #dee2e6;
    }

    * {
        box-sizing: border-box;
    }

    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        margin: 0;
        padding: 0;
        background: var(--bg-light);
        color: #333;
        line-height: 1.6;
    }

    .header {
        background: linear-gradient(135deg, var(--cost-purple), var(--cost-blue));
        color: white;
        padding: 20px 40px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }

    .header h1 {
        margin: 0 0 10px 0;
        font-size: 1.8em;
    }

    .header .subtitle {
        opacity: 0.9;
        font-size: 1em;
    }

    .nav-bar {
        background: white;
        padding: 10px 40px;
        border-bottom: 1px solid var(--border-color);
        display: flex;
        gap: 20px;
        flex-wrap: wrap;
    }

    .nav-bar a {
        color: var(--cost-purple);
        text-decoration: none;
        padding: 8px 16px;
        border-radius: 4px;
        transition: all 0.2s;
    }

    .nav-bar a:hover {
        background: var(--cost-purple);
        color: white;
    }

    .container {
        max-width: 1600px;
        margin: 0 auto;
        padding: 20px 40px;
    }

    /* Tab Styles */
    .tabs {
        display: flex;
        flex-wrap: wrap;
        gap: 5px;
        margin-bottom: 20px;
        background: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }

    .tab-btn {
        padding: 10px 20px;
        border: none;
        background: var(--bg-light);
        cursor: pointer;
        border-radius: 4px;
        font-size: 0.9em;
        transition: all 0.2s;
        color: #333;
    }

    .tab-btn:hover {
        background: var(--cost-purple-light);
        color: white;
    }

    .tab-btn.active {
        background: var(--cost-purple);
        color: white;
    }

    .tab-content {
        display: none;
        background: white;
        padding: 30px;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }

    .tab-content.active {
        display: block;
    }

    /* Stats Grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin: 20px 0;
    }

    .stat-card {
        background: linear-gradient(135deg, var(--cost-purple), var(--cost-blue));
        color: white;
        padding: 20px;
        border-radius: 8px;
        text-align: center;
    }

    .stat-card .value {
        font-size: 2.5em;
        font-weight: bold;
        display: block;
    }

    .stat-card .label {
        opacity: 0.9;
        font-size: 0.9em;
    }

    /* Objective Cards */
    .objective-card {
        background: white;
        border: 1px solid var(--border-color);
        border-radius: 8px;
        margin-bottom: 20px;
        overflow: hidden;
    }

    .objective-header {
        background: var(--cost-purple);
        color: white;
        padding: 15px 20px;
        cursor: pointer;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .objective-header:hover {
        background: var(--cost-purple-light);
    }

    .objective-title {
        font-weight: bold;
        flex: 1;
    }

    .objective-badges {
        display: flex;
        gap: 10px;
    }

    .badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8em;
        font-weight: bold;
    }

    .badge-success {
        background: var(--cost-green);
        color: white;
    }

    .badge-warning {
        background: var(--cost-orange);
        color: white;
    }

    .badge-info {
        background: var(--cost-blue);
        color: white;
    }

    .objective-body {
        padding: 20px;
        display: none;
    }

    .objective-body.expanded {
        display: block;
    }

    .proof-text {
        background: var(--bg-light);
        padding: 20px;
        border-radius: 8px;
        margin-top: 15px;
        border-left: 4px solid var(--cost-purple);
        font-size: 0.95em;
        line-height: 1.8;
        max-height: 800px;
        overflow-y: auto;
    }

    .proof-text p {
        margin: 0 0 1em 0;
    }

    /* Deliverable Table */
    .deliverables-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 20px;
    }

    .deliverables-table th,
    .deliverables-table td {
        padding: 12px 15px;
        text-align: left;
        border-bottom: 1px solid var(--border-color);
    }

    .deliverables-table th {
        background: var(--cost-purple);
        color: white;
    }

    .deliverables-table tr:hover {
        background: var(--bg-light);
    }

    /* Publications */
    .publication-item {
        background: white;
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 15px 20px;
        margin-bottom: 10px;
    }

    .publication-item:hover {
        border-color: var(--cost-purple);
    }

    .pub-title {
        font-weight: bold;
        color: var(--cost-purple);
        margin-bottom: 5px;
    }

    .pub-authors {
        color: var(--cost-gray);
        font-size: 0.9em;
    }

    .pub-doi {
        color: var(--cost-blue);
        font-size: 0.85em;
    }

    .pub-doi a {
        color: inherit;
    }

    /* Page Content Display */
    .page-section {
        background: white;
        border: 1px solid var(--border-color);
        border-radius: 8px;
        margin-bottom: 20px;
        overflow: hidden;
    }

    .page-header {
        background: var(--cost-blue);
        color: white;
        padding: 10px 20px;
        font-weight: bold;
    }

    .page-content {
        padding: 20px;
        white-space: pre-wrap;
        font-family: 'Courier New', monospace;
        font-size: 0.9em;
        max-height: 600px;
        overflow-y: auto;
        background: #f5f5f5;
    }

    /* Comparison Styles */
    .comparison-row {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        margin-bottom: 30px;
    }

    .comparison-column {
        background: white;
        border: 1px solid var(--border-color);
        border-radius: 8px;
        overflow: hidden;
    }

    .comparison-header {
        padding: 15px 20px;
        font-weight: bold;
        color: white;
    }

    .comparison-header.midterm {
        background: var(--cost-blue);
    }

    .comparison-header.final {
        background: var(--cost-purple);
    }

    .comparison-content {
        padding: 20px;
        max-height: 400px;
        overflow-y: auto;
    }

    .change-indicator {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 0.85em;
        font-weight: bold;
    }

    .change-positive {
        background: #d4edda;
        color: #155724;
    }

    .change-negative {
        background: #f8d7da;
        color: #721c24;
    }

    .change-neutral {
        background: #e2e3e5;
        color: #383d41;
    }

    /* Search and Filter */
    .search-box {
        width: 100%;
        padding: 12px 20px;
        border: 2px solid var(--border-color);
        border-radius: 8px;
        font-size: 1em;
        margin-bottom: 20px;
    }

    .search-box:focus {
        outline: none;
        border-color: var(--cost-purple);
    }

    /* Leadership */
    .leadership-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 20px;
    }

    .leader-card {
        background: white;
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 20px;
    }

    .leader-card h4 {
        color: var(--cost-purple);
        margin: 0 0 10px 0;
    }

    .leader-info {
        color: var(--cost-gray);
        font-size: 0.9em;
    }

    /* Footer */
    .footer {
        background: var(--cost-purple);
        color: white;
        text-align: center;
        padding: 20px;
        margin-top: 40px;
    }

    .footer a {
        color: white;
        text-decoration: underline;
    }

    /* Expand/Collapse All */
    .expand-controls {
        margin-bottom: 15px;
    }

    .expand-controls button {
        padding: 8px 16px;
        margin-right: 10px;
        border: 1px solid var(--cost-purple);
        background: white;
        color: var(--cost-purple);
        border-radius: 4px;
        cursor: pointer;
    }

    .expand-controls button:hover {
        background: var(--cost-purple);
        color: white;
    }
</style>
"""

JS_SCRIPTS = """
<script>
    // Tab switching
    function showTab(tabId) {
        document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.getElementById(tabId).classList.add('active');
        event.target.classList.add('active');
    }

    // Toggle objective expansion
    function toggleObjective(id) {
        const body = document.getElementById('obj-body-' + id);
        body.classList.toggle('expanded');
    }

    // Expand/Collapse all objectives
    function expandAll() {
        document.querySelectorAll('.objective-body').forEach(b => b.classList.add('expanded'));
    }

    function collapseAll() {
        document.querySelectorAll('.objective-body').forEach(b => b.classList.remove('expanded'));
    }

    // Publication search
    function searchPublications() {
        const query = document.getElementById('pub-search').value.toLowerCase();
        document.querySelectorAll('.publication-item').forEach(item => {
            const text = item.textContent.toLowerCase();
            item.style.display = text.includes(query) ? 'block' : 'none';
        });
    }

    // Page navigation
    function goToPage(pageNum) {
        document.querySelectorAll('.page-section').forEach(p => p.style.display = 'none');
        document.getElementById('page-' + pageNum).style.display = 'block';
    }
</script>
"""


def escape_html(text):
    """Escape HTML special characters."""
    if not text:
        return ""
    return (str(text)
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#39;'))


def generate_report_html(report_data, is_final=True):
    """Generate a complete HTML page for a report with tabbed interface."""
    report_type = "Final Achievement Report" if is_final else "Mid-Term Report (24 months)"
    period = report_data["metadata"]["period"]

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>COST CA19130 - {report_type} (Full)</title>
    {CSS_STYLES}
</head>
<body>
    <div class="header">
        <h1>COST Action CA19130: {report_type}</h1>
        <div class="subtitle">Fintech and Artificial Intelligence in Finance | Period: {period} | {report_data['metadata']['pages']} Pages</div>
    </div>

    <div class="nav-bar">
        <a href="index.html">Home</a>
        <a href="final-action-chair-report-full.html">Final Report (Full)</a>
        <a href="midterm-action-chair-report-full.html">Mid-Term Report (Full)</a>
        <a href="comparison-action-chair-full.html">Comparison (Full)</a>
        <a href="final-action-chair-report.html">Final Report (Summary)</a>
        <a href="midterm-action-chair-report.html">Mid-Term Report (Summary)</a>
    </div>

    <div class="container">
        <div class="tabs">
            <button class="tab-btn active" onclick="showTab('summary')">Summary</button>
            <button class="tab-btn" onclick="showTab('leadership')">Leadership</button>
            <button class="tab-btn" onclick="showTab('objectives')">Objectives ({len(report_data['objectives'])})</button>
            <button class="tab-btn" onclick="showTab('deliverables')">Deliverables ({len(report_data['deliverables'])})</button>
            <button class="tab-btn" onclick="showTab('publications')">Publications ({len(report_data['publications'])})</button>
            <button class="tab-btn" onclick="showTab('stsms')">STSMs & VMGs</button>
            <button class="tab-btn" onclick="showTab('impacts')">Impacts</button>
            <button class="tab-btn" onclick="showTab('pages')">All Pages ({report_data['metadata']['pages']})</button>
        </div>
"""
    # Summary Tab
    stats = report_data["summary"]["stats"]
    html += f"""
        <div id="summary" class="tab-content active">
            <h2>Summary Statistics</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <span class="value">{stats.get('researchers', 'N/A')}</span>
                    <span class="label">Researchers</span>
                </div>
                <div class="stat-card">
                    <span class="value">{stats.get('countries', 'N/A')}</span>
                    <span class="label">Countries</span>
                </div>
                <div class="stat-card">
                    <span class="value">{stats.get('cost_countries', 'N/A')}</span>
                    <span class="label">COST Countries</span>
                </div>
                <div class="stat-card">
                    <span class="value">{stats.get('conferences', 'N/A')}</span>
                    <span class="label">Conferences</span>
                </div>
                <div class="stat-card">
                    <span class="value">{stats.get('participants', 'N/A'):,}</span>
                    <span class="label">Event Participants</span>
                </div>
                <div class="stat-card">
                    <span class="value">{stats.get('citations', 'N/A'):,}</span>
                    <span class="label">Citations</span>
                </div>
            </div>

            <h3>Main Objective</h3>
            <p>{escape_html(report_data['summary'].get('main_objective', 'N/A'))}</p>

            <h3>Description</h3>
            <div class="proof-text">{escape_html(report_data['summary'].get('description', 'N/A'))}</div>

            <h3>Website</h3>
            <p><a href="{report_data['summary'].get('website', '#')}" target="_blank">{report_data['summary'].get('website', 'N/A')}</a></p>
        </div>
"""

    # Leadership Tab
    leadership = report_data.get("leadership", {})
    html += """
        <div id="leadership" class="tab-content">
            <h2>Leadership Positions</h2>
            <div class="leadership-grid">
"""
    if leadership.get("chair"):
        chair = leadership["chair"]
        html += f"""
                <div class="leader-card">
                    <h4>Action Chair</h4>
                    <div><strong>{escape_html(chair.get('name', 'N/A'))}</strong></div>
                    <div class="leader-info">{escape_html(chair.get('email', ''))}</div>
                    <div class="leader-info">Country: {escape_html(chair.get('country', ''))}</div>
                </div>
"""
    if leadership.get("vice_chair"):
        vc = leadership["vice_chair"]
        html += f"""
                <div class="leader-card">
                    <h4>Action Vice-Chair</h4>
                    <div><strong>{escape_html(vc.get('name', 'N/A'))}</strong></div>
                    <div class="leader-info">{escape_html(vc.get('email', ''))}</div>
                    <div class="leader-info">Country: {escape_html(vc.get('country', ''))}</div>
                </div>
"""
    for wg in leadership.get("wg_leaders", []):
        html += f"""
                <div class="leader-card">
                    <h4>WG{wg.get('wg_number', '')} Leader: {escape_html(wg.get('wg_title', '')[:50])}</h4>
                    <div><strong>{escape_html(wg.get('name', 'N/A'))}</strong></div>
                    <div class="leader-info">{escape_html(wg.get('email', ''))}</div>
                    <div class="leader-info">Country: {escape_html(wg.get('country', ''))} | Participants: {wg.get('participants', 'N/A')}</div>
                </div>
"""
    # Add Other Leadership Positions
    for pos in leadership.get("other_positions", []):
        html += f"""
                <div class="leader-card">
                    <h4>{escape_html(pos.get('position', 'Other Position'))}</h4>
                    <div><strong>{escape_html(pos.get('name', 'N/A'))}</strong></div>
                    <div class="leader-info">{escape_html(pos.get('email', ''))}</div>
                    <div class="leader-info">Country: {escape_html(pos.get('country', ''))}</div>
                </div>
"""
    html += """
            </div>

            <h3>Participating Countries</h3>
            <p>"""
    participants = report_data.get("participants", {})
    countries = participants.get("countries", [])
    html += f"<strong>{len(countries)} countries</strong>: "
    html += ", ".join([f"{c['code']} ({c['date']})" for c in countries])
    html += """</p>
        </div>
"""

    # Objectives Tab
    html += f"""
        <div id="objectives" class="tab-content">
            <h2>MoU Objectives ({len(report_data['objectives'])} Total)</h2>
            <div class="expand-controls">
                <button onclick="expandAll()">Expand All</button>
                <button onclick="collapseAll()">Collapse All</button>
            </div>
"""
    for obj in report_data["objectives"]:
        achievement_class = "badge-success" if "76" in obj.get("achievement", "") else "badge-warning" if "51" in obj.get("achievement", "") else "badge-info"
        html += f"""
            <div class="objective-card">
                <div class="objective-header" onclick="toggleObjective({obj['number']})">
                    <span class="objective-title">Objective {obj['number']}: {escape_html(obj.get('title', '')[:100])}...</span>
                    <div class="objective-badges">
                        <span class="badge {achievement_class}">{obj.get('achievement', 'N/A')}</span>
                        <span class="badge badge-info">{obj.get('dependence', 'N/A')}</span>
                    </div>
                </div>
                <div id="obj-body-{obj['number']}" class="objective-body">
                    <h4>Full Objective Title</h4>
                    <p>{escape_html(obj.get('title', ''))}</p>

                    <h4>Type of Objective</h4>
                    <p>{', '.join(obj.get('type', []))}</p>

                    <h4>Level of Achievement: {obj.get('achievement', 'N/A')}</h4>
                    <h4>Dependence on Action Networking: {obj.get('dependence', 'N/A')}</h4>

                    <h4>Proof of Achievement (Full Text)</h4>
                    <div class="proof-text">{escape_html(obj.get('proof_text', 'No proof text available'))}</div>
                </div>
            </div>
"""
    html += """
        </div>
"""

    # Deliverables Tab
    html += f"""
        <div id="deliverables" class="tab-content">
            <h2>Deliverables ({len(report_data['deliverables'])} Total)</h2>
            <table class="deliverables-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Deliverable Title</th>
                        <th>Status</th>
                        <th>Dependence</th>
                        <th>Proof</th>
                    </tr>
                </thead>
                <tbody>
"""
    for d in report_data["deliverables"]:
        status_class = "badge-success" if d.get("status") == "Delivered" else "badge-warning"
        html += f"""
                    <tr>
                        <td>{d.get('number', '')}</td>
                        <td>{escape_html(d.get('title', ''))}</td>
                        <td><span class="badge {status_class}">{d.get('status', 'N/A')}</span></td>
                        <td>{d.get('dependence', 'N/A')}</td>
                        <td><a href="{d.get('proof_url', '#')}" target="_blank">Link</a></td>
                    </tr>
"""
    html += """
                </tbody>
            </table>
        </div>
"""

    # Publications Tab
    html += f"""
        <div id="publications" class="tab-content">
            <h2>Co-authored Publications ({len(report_data['publications'])} Total)</h2>
            <input type="text" id="pub-search" class="search-box" placeholder="Search publications by title, author, or DOI..." oninput="searchPublications()">
"""
    for pub in report_data["publications"]:
        html += f"""
            <div class="publication-item">
                <div class="pub-title">{pub.get('number', '')}. {escape_html(pub.get('title', 'Untitled'))}</div>
                <div class="pub-authors">{escape_html(pub.get('authors', 'Unknown authors'))}</div>
                <div class="pub-doi"><a href="https://doi.org/{pub.get('doi', '').replace('doi:', '')}" target="_blank">{pub.get('doi', '')}</a></div>
                <div style="margin-top: 5px; font-size: 0.85em; color: var(--cost-gray);">
                    Type: {pub.get('type', 'N/A')} | Published in: {escape_html(pub.get('published_in', 'N/A'))} | Countries: {', '.join(pub.get('countries', []))}
                </div>
            </div>
"""
    html += """
        </div>
"""

    # STSMs & VMGs Tab
    stsms_vmgs = report_data.get("stsms_vmgs", {})
    html += """
        <div id="stsms" class="tab-content">
            <h2>Short-Term Scientific Missions (STSMs) & Virtual Mobility Grants (VMGs)</h2>
"""
    if stsms_vmgs.get("stsms"):
        html += "<h3>STSMs</h3>"
        for stsm in stsms_vmgs["stsms"]:
            html += f"""<div class="proof-text">{escape_html(stsm.get('description', ''))}</div>"""

    if stsms_vmgs.get("vmgs"):
        html += "<h3>Virtual Mobility Grants</h3>"
        for vmg in stsms_vmgs["vmgs"]:
            html += f"""
            <div class="publication-item">
                <div class="pub-title">{escape_html(vmg.get('researcher', ''))}</div>
                <div class="pub-authors">{escape_html(vmg.get('description', ''))}</div>
            </div>
"""
    html += """
        </div>
"""

    # Impacts Tab
    impacts = report_data.get("impacts", {})
    html += f"""
        <div id="impacts" class="tab-content">
            <h2>Career Impacts & Achievements</h2>

            <h3>Career Benefits</h3>
            <div class="proof-text">{escape_html(impacts.get('career_benefits', 'N/A'))}</div>

            <h3>Experience Level</h3>
            <p>Career benefits mainly for researchers with: <strong>{impacts.get('experience_level', 'N/A')}</strong></p>

            <h3>Stakeholder Engagement</h3>
            <div class="proof-text">{escape_html(impacts.get('stakeholder_engagement', 'N/A'))}</div>

            <h3>Dissemination Approach</h3>
            <div class="proof-text">{escape_html(impacts.get('dissemination_approach', 'N/A'))}</div>
        </div>
"""

    # All Pages Tab
    html += f"""
        <div id="pages" class="tab-content">
            <h2>Full Report Content ({report_data['metadata']['pages']} Pages)</h2>
            <p>Select a page to view its raw content:</p>
            <div style="margin-bottom: 20px;">
"""
    page_nums = sorted([int(p) for p in report_data.get("raw_pages", {}).keys()])
    for p in page_nums:
        html += f'<button onclick="goToPage({p})" style="margin: 2px; padding: 5px 10px; cursor: pointer;">Page {p}</button>'

    html += """
            </div>
"""
    for p in page_nums:
        content = report_data["raw_pages"].get(str(p), "")
        html += f"""
            <div id="page-{p}" class="page-section" style="display: {'block' if p == 1 else 'none'};">
                <div class="page-header">Page {p}</div>
                <div class="page-content">{escape_html(content)}</div>
            </div>
"""
    html += """
        </div>
"""

    # Close container and add footer
    html += f"""
    </div>

    <div class="footer">
        <p>COST Action CA19130: Fintech and Artificial Intelligence in Finance</p>
        <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")} |
           <a href="https://www.fintech-ai-finance.com/" target="_blank">Action Website</a> |
           <a href="https://github.com/Digital-AI-Finance/COST-Fintech-AI-in-Finance" target="_blank">GitHub Repository</a>
        </p>
    </div>

    {JS_SCRIPTS}
</body>
</html>
"""
    return html


def generate_comparison_html(comparison_data, final_data, midterm_data):
    """Generate a full side-by-side comparison HTML page."""
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>COST CA19130 - Full Comparison: Mid-Term vs Final Report</title>
    {CSS_STYLES}
    <style>
        .summary-comparison {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}

        .comparison-stat {{
            background: white;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }}

        .comparison-stat .values {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin: 10px 0;
        }}

        .comparison-stat .midterm-val {{
            color: var(--cost-blue);
            font-size: 1.5em;
            font-weight: bold;
        }}

        .comparison-stat .final-val {{
            color: var(--cost-purple);
            font-size: 1.5em;
            font-weight: bold;
        }}

        .comparison-stat .arrow {{
            font-size: 1.5em;
            color: var(--cost-green);
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>COST Action CA19130: Full Report Comparison</h1>
        <div class="subtitle">Mid-Term Report (24 months) vs Final Report (48 months) | Side-by-Side Analysis</div>
    </div>

    <div class="nav-bar">
        <a href="index.html">Home</a>
        <a href="final-action-chair-report-full.html">Final Report (Full)</a>
        <a href="midterm-action-chair-report-full.html">Mid-Term Report (Full)</a>
        <a href="comparison-action-chair-full.html">Comparison (Full)</a>
        <a href="comparison-action-chair.html">Comparison (Summary)</a>
    </div>

    <div class="container">
        <div class="tabs">
            <button class="tab-btn active" onclick="showTab('overview')">Overview</button>
"""
    # Add tabs for each objective
    for obj in comparison_data["objectives_comparison"]:
        html += f'<button class="tab-btn" onclick="showTab(\'obj-{obj["number"]}\')">Obj {obj["number"]}</button>'

    html += """
            <button class="tab-btn" onclick="showTab('deliverables-comp')">Deliverables</button>
            <button class="tab-btn" onclick="showTab('publications-comp')">Publications</button>
        </div>
"""

    # Overview Tab
    summary_comp = comparison_data.get("summary_comparison", {})
    html += f"""
        <div id="overview" class="tab-content active">
            <h2>Summary Comparison</h2>
            <div class="summary-comparison">
                <div class="comparison-stat">
                    <div class="label">Researchers</div>
                    <div class="values">
                        <span class="midterm-val">{summary_comp.get('researchers', {}).get('midterm', 'N/A')}</span>
                        <span class="arrow">-></span>
                        <span class="final-val">{summary_comp.get('researchers', {}).get('final', 'N/A')}</span>
                    </div>
                    <div class="change-indicator change-positive">+{summary_comp.get('researchers', {}).get('change', 0)} researchers</div>
                </div>
                <div class="comparison-stat">
                    <div class="label">Countries</div>
                    <div class="values">
                        <span class="midterm-val">{summary_comp.get('countries', {}).get('midterm', 'N/A')}</span>
                        <span class="arrow">-></span>
                        <span class="final-val">{summary_comp.get('countries', {}).get('final', 'N/A')}</span>
                    </div>
                    <div class="change-indicator change-positive">+{summary_comp.get('countries', {}).get('change', 0)} countries</div>
                </div>
                <div class="comparison-stat">
                    <div class="label">Publications</div>
                    <div class="values">
                        <span class="midterm-val">{comparison_data.get('publications_comparison', {}).get('midterm_count', 'N/A')}</span>
                        <span class="arrow">-></span>
                        <span class="final-val">{comparison_data.get('publications_comparison', {}).get('final_count', 'N/A')}</span>
                    </div>
                    <div class="change-indicator change-positive">+{comparison_data.get('publications_comparison', {}).get('new_publications', 0)} new</div>
                </div>
                <div class="comparison-stat">
                    <div class="label">Objectives</div>
                    <div class="values">
                        <span class="midterm-val">{len(midterm_data['objectives'])}</span>
                        <span class="arrow">-></span>
                        <span class="final-val">{len(final_data['objectives'])}</span>
                    </div>
                    <div class="change-indicator change-neutral">All 16 objectives tracked</div>
                </div>
            </div>

            <h3>All Objectives Overview</h3>
            <table class="deliverables-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Objective Title</th>
                        <th>Mid-Term</th>
                        <th>Final</th>
                        <th>Change</th>
                    </tr>
                </thead>
                <tbody>
"""
    for obj in comparison_data["objectives_comparison"]:
        changed = obj.get("achievement_changed", False)
        change_badge = '<span class="badge badge-success">Changed</span>' if changed else '<span class="badge badge-info">Same</span>'
        html += f"""
                    <tr>
                        <td>{obj.get('number', '')}</td>
                        <td>{escape_html(obj.get('title', '')[:80])}...</td>
                        <td>{obj.get('midterm_achievement', 'N/A')}</td>
                        <td>{obj.get('final_achievement', 'N/A')}</td>
                        <td>{change_badge}</td>
                    </tr>
"""
    html += """
                </tbody>
            </table>
        </div>
"""

    # Individual Objective Comparison Tabs
    for obj in comparison_data["objectives_comparison"]:
        html += f"""
        <div id="obj-{obj['number']}" class="tab-content">
            <h2>Objective {obj['number']} Comparison</h2>
            <h3>{escape_html(obj.get('title', ''))}</h3>

            <div style="margin: 20px 0;">
                <span class="badge badge-info">Mid-Term: {obj.get('midterm_achievement', 'N/A')}</span>
                <span style="margin: 0 10px;">-></span>
                <span class="badge badge-success">Final: {obj.get('final_achievement', 'N/A')}</span>
            </div>

            <div class="comparison-row">
                <div class="comparison-column">
                    <div class="comparison-header midterm">Mid-Term Report (24 months)</div>
                    <div class="comparison-content">
                        <h4>Achievement Level: {obj.get('midterm_achievement', 'N/A')}</h4>
                        <div class="proof-text">{escape_html(obj.get('midterm_proof', 'No proof text available'))}</div>
                    </div>
                </div>
                <div class="comparison-column">
                    <div class="comparison-header final">Final Report (48 months)</div>
                    <div class="comparison-content">
                        <h4>Achievement Level: {obj.get('final_achievement', 'N/A')}</h4>
                        <div class="proof-text">{escape_html(obj.get('final_proof', 'No proof text available'))}</div>
                    </div>
                </div>
            </div>
        </div>
"""

    # Deliverables Comparison Tab
    html += f"""
        <div id="deliverables-comp" class="tab-content">
            <h2>Deliverables Comparison</h2>
            <table class="deliverables-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Deliverable</th>
                        <th>Mid-Term Status</th>
                        <th>Final Status</th>
                        <th>Changed</th>
                    </tr>
                </thead>
                <tbody>
"""
    for d in comparison_data.get("deliverables_comparison", []):
        changed = d.get("status_changed", False)
        change_badge = '<span class="badge badge-success">Yes</span>' if changed else '<span class="badge badge-info">No</span>'
        html += f"""
                    <tr>
                        <td>{d.get('number', '')}</td>
                        <td>{escape_html(d.get('title', '')[:100])}</td>
                        <td>{d.get('midterm_status', 'N/A')}</td>
                        <td>{d.get('final_status', 'N/A')}</td>
                        <td>{change_badge}</td>
                    </tr>
"""
    html += """
                </tbody>
            </table>
        </div>
"""

    # Publications Comparison Tab
    pub_comp = comparison_data.get("publications_comparison", {})
    html += f"""
        <div id="publications-comp" class="tab-content">
            <h2>Publications Comparison</h2>
            <div class="summary-comparison">
                <div class="comparison-stat">
                    <div class="label">Mid-Term Publications</div>
                    <span class="midterm-val" style="font-size: 3em;">{pub_comp.get('midterm_count', 'N/A')}</span>
                </div>
                <div class="comparison-stat">
                    <div class="label">Final Publications</div>
                    <span class="final-val" style="font-size: 3em;">{pub_comp.get('final_count', 'N/A')}</span>
                </div>
                <div class="comparison-stat">
                    <div class="label">New Publications</div>
                    <span style="font-size: 3em; color: var(--cost-green);">+{pub_comp.get('new_publications', 0)}</span>
                </div>
            </div>

            <h3>Publication Growth</h3>
            <p>The Action has grown from <strong>{pub_comp.get('midterm_count', 'N/A')}</strong> publications at mid-term
               to <strong>{pub_comp.get('final_count', 'N/A')}</strong> publications at the final report,
               representing <strong>{pub_comp.get('new_publications', 0)}</strong> new co-authored publications.</p>

            <p>View full publication lists:</p>
            <ul>
                <li><a href="final-action-chair-report-full.html#publications">Final Report Publications ({pub_comp.get('final_count', 'N/A')})</a></li>
                <li><a href="midterm-action-chair-report-full.html#publications">Mid-Term Report Publications ({pub_comp.get('midterm_count', 'N/A')})</a></li>
            </ul>
        </div>
"""

    # Close container and add footer
    html += f"""
    </div>

    <div class="footer">
        <p>COST Action CA19130: Fintech and Artificial Intelligence in Finance</p>
        <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")} |
           <a href="https://www.fintech-ai-finance.com/" target="_blank">Action Website</a> |
           <a href="https://github.com/Digital-AI-Finance/COST-Fintech-AI-in-Finance" target="_blank">GitHub Repository</a>
        </p>
    </div>

    {JS_SCRIPTS}
</body>
</html>
"""
    return html


def main():
    """Main HTML generation function."""
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / "data"

    print("=" * 60)
    print("COST Action CA19130 HTML Generation")
    print("=" * 60)

    # Load JSON data
    print("\n[1/4] Loading JSON data...")
    with open(data_dir / "final_report_full.json", 'r', encoding='utf-8') as f:
        final_data = json.load(f)
    with open(data_dir / "midterm_report_full.json", 'r', encoding='utf-8') as f:
        midterm_data = json.load(f)
    with open(data_dir / "report_comparison.json", 'r', encoding='utf-8') as f:
        comparison_data = json.load(f)
    print("  -> Data loaded successfully")

    # Generate Final Report HTML
    print("\n[2/4] Generating Final Report HTML...")
    final_html = generate_report_html(final_data, is_final=True)
    final_path = base_dir / "final-action-chair-report-full.html"
    with open(final_path, 'w', encoding='utf-8') as f:
        f.write(final_html)
    print(f"  -> Saved: {final_path}")
    print(f"  -> Size: {len(final_html):,} characters")

    # Generate Mid-Term Report HTML
    print("\n[3/4] Generating Mid-Term Report HTML...")
    midterm_html = generate_report_html(midterm_data, is_final=False)
    midterm_path = base_dir / "midterm-action-chair-report-full.html"
    with open(midterm_path, 'w', encoding='utf-8') as f:
        f.write(midterm_html)
    print(f"  -> Saved: {midterm_path}")
    print(f"  -> Size: {len(midterm_html):,} characters")

    # Generate Comparison HTML
    print("\n[4/4] Generating Comparison HTML...")
    comparison_html = generate_comparison_html(comparison_data, final_data, midterm_data)
    comparison_path = base_dir / "comparison-action-chair-full.html"
    with open(comparison_path, 'w', encoding='utf-8') as f:
        f.write(comparison_html)
    print(f"  -> Saved: {comparison_path}")
    print(f"  -> Size: {len(comparison_html):,} characters")

    print("\n" + "=" * 60)
    print("HTML Generation Complete!")
    print("=" * 60)
    print(f"\nGenerated files:")
    print(f"  - {final_path.name}")
    print(f"  - {midterm_path.name}")
    print(f"  - {comparison_path.name}")


if __name__ == "__main__":
    main()
