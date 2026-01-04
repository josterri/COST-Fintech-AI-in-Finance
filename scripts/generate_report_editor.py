"""
Generate an interactive Report Editor HTML page.
Allows editing of all report sections with local save functionality.
Full parity with JSON data structure.
"""

import json
from pathlib import Path
from datetime import datetime


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


def generate_report_editor_html(final_data):
    """Generate an interactive report editor HTML page with full JSON coverage."""

    # Prepare data for JavaScript
    report_json = json.dumps(final_data, indent=2)

    # Extract counts for sidebar
    num_objectives = len(final_data.get('objectives', []))
    num_deliverables = len(final_data.get('deliverables', []))
    num_publications = len(final_data.get('publications', []))
    num_countries = len(final_data.get('participants', {}).get('countries', []))
    num_events = len(final_data.get('events', []))

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>COST CA19130 - Report Editor</title>
    <style>
        :root {{
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
        }}

        * {{ box-sizing: border-box; margin: 0; padding: 0; }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: var(--bg-light);
            color: #333;
            line-height: 1.6;
        }}

        .header {{
            background: linear-gradient(135deg, var(--cost-purple), var(--cost-orange));
            color: white;
            padding: 20px 40px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }}

        .header-content {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1800px;
            margin: 0 auto;
        }}

        .header h1 {{ font-size: 1.6em; }}
        .header .subtitle {{ opacity: 0.9; font-size: 0.95em; }}

        .header-actions {{
            display: flex;
            gap: 10px;
        }}

        .btn {{
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.95em;
            font-weight: 500;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }}

        .btn-primary {{ background: white; color: var(--cost-purple); }}
        .btn-primary:hover {{ background: var(--bg-light); transform: translateY(-1px); }}
        .btn-success {{ background: var(--cost-green); color: white; }}
        .btn-success:hover {{ background: #218838; }}
        .btn-warning {{ background: var(--cost-orange); color: white; }}
        .btn-danger {{ background: var(--cost-red); color: white; }}

        .nav-bar {{
            background: white;
            padding: 12px 40px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }}

        .nav-bar a {{
            color: var(--cost-purple);
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 4px;
            transition: all 0.2s;
        }}

        .nav-bar a:hover, .nav-bar a.active {{ background: var(--cost-purple); color: white; }}

        .main-container {{
            display: flex;
            max-width: 1800px;
            margin: 0 auto;
            min-height: calc(100vh - 150px);
        }}

        .sidebar {{
            width: 280px;
            background: white;
            border-right: 1px solid var(--border-color);
            padding: 20px 0;
            position: sticky;
            top: 80px;
            height: fit-content;
            max-height: calc(100vh - 100px);
            overflow-y: auto;
        }}

        .sidebar-section {{
            padding: 10px 20px;
            cursor: pointer;
            transition: all 0.2s;
            border-left: 3px solid transparent;
        }}

        .sidebar-section:hover {{ background: var(--bg-light); border-left-color: var(--cost-purple-light); }}
        .sidebar-section.active {{ background: #f0e6f6; border-left-color: var(--cost-purple); font-weight: 500; }}
        .sidebar-section.modified::after {{ content: '*'; color: var(--cost-orange); margin-left: 5px; font-weight: bold; }}

        .sidebar-group {{
            font-size: 0.8em;
            text-transform: uppercase;
            color: var(--cost-gray);
            padding: 15px 20px 8px;
            letter-spacing: 1px;
        }}

        .editor-area {{ flex: 1; padding: 30px 40px; }}

        .editor-panel {{
            display: none;
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}

        .editor-panel.active {{ display: block; }}
        .editor-panel h2 {{ color: var(--cost-purple); margin-bottom: 20px; padding-bottom: 15px; border-bottom: 2px solid var(--bg-light); }}
        .editor-panel h3 {{ margin: 30px 0 15px; color: var(--cost-purple); }}

        .form-group {{ margin-bottom: 25px; }}
        .form-group label {{ display: block; font-weight: 500; margin-bottom: 8px; color: #555; }}
        .form-group input, .form-group select {{ width: 100%; padding: 12px 15px; border: 2px solid var(--border-color); border-radius: 8px; font-size: 1em; transition: border-color 0.2s; }}
        .form-group input:focus, .form-group select:focus, .form-group textarea:focus {{ outline: none; border-color: var(--cost-purple); }}
        .form-group textarea {{ width: 100%; padding: 15px; border: 2px solid var(--border-color); border-radius: 8px; font-size: 1em; font-family: inherit; resize: vertical; min-height: 150px; line-height: 1.7; }}
        .form-group textarea.large {{ min-height: 300px; }}
        .form-group input[readonly] {{ background: var(--bg-light); color: var(--cost-gray); }}

        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
        .stats-grid .form-group {{ margin-bottom: 0; }}

        .objective-editor {{ border: 1px solid var(--border-color); border-radius: 8px; margin-bottom: 15px; overflow: hidden; }}
        .objective-header {{ background: var(--cost-purple); color: white; padding: 12px 20px; cursor: pointer; display: flex; justify-content: space-between; align-items: center; }}
        .objective-header:hover {{ background: var(--cost-purple-light); }}
        .objective-body {{ padding: 20px; display: none; background: #fafafa; }}
        .objective-body.expanded {{ display: block; }}

        .status-bar {{
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: white;
            border-top: 1px solid var(--border-color);
            padding: 12px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 100;
            box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
        }}

        .status-indicator {{ display: flex; align-items: center; gap: 10px; }}
        .status-dot {{ width: 10px; height: 10px; border-radius: 50%; }}
        .status-dot.saved {{ background: var(--cost-green); }}
        .status-dot.modified {{ background: var(--cost-orange); }}

        .toast {{
            position: fixed;
            bottom: 80px;
            right: 20px;
            padding: 15px 25px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 1000;
            transform: translateX(150%);
            transition: transform 0.3s ease;
        }}
        .toast.show {{ transform: translateX(0); }}
        .toast.success {{ background: var(--cost-green); }}
        .toast.error {{ background: var(--cost-red); }}
        .toast.info {{ background: var(--cost-blue); }}

        .data-row {{
            display: grid;
            gap: 15px;
            padding: 12px 15px;
            background: var(--bg-light);
            border-radius: 8px;
            margin-bottom: 10px;
            align-items: center;
        }}
        .data-row input, .data-row select {{ padding: 8px 12px; }}

        .deliverable-row {{ grid-template-columns: 50px 1fr 120px 120px 1fr; }}
        .country-row {{ grid-template-columns: 80px 1fr 40px; }}
        .event-row {{ grid-template-columns: 50px 1fr 40px; }}
        .publication-row {{ grid-template-columns: 50px 1fr; }}
        .other-pos-row {{ grid-template-columns: 1fr 1fr 1fr 100px; }}

        .add-btn {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 10px 20px;
            background: var(--bg-light);
            border: 2px dashed var(--border-color);
            border-radius: 8px;
            cursor: pointer;
            color: var(--cost-gray);
            transition: all 0.2s;
            margin-top: 15px;
        }}
        .add-btn:hover {{ border-color: var(--cost-purple); color: var(--cost-purple); }}

        .delete-btn {{
            background: var(--cost-red);
            color: white;
            border: none;
            border-radius: 4px;
            padding: 5px 10px;
            cursor: pointer;
            font-size: 0.85em;
        }}
        .delete-btn:hover {{ background: #c82333; }}

        .meta-display {{
            background: var(--bg-light);
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 10px;
        }}
        .meta-display strong {{ color: var(--cost-purple); }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <div>
                <h1>COST CA19130 Report Editor</h1>
                <div class="subtitle">Edit and save the Final Achievement Report - Full JSON Coverage</div>
            </div>
            <div class="header-actions">
                <button class="btn btn-primary" onclick="resetToOriginal()">Reset</button>
                <button class="btn btn-primary" onclick="loadFromFile()">Load</button>
                <button class="btn btn-success" onclick="saveToLocalStorage()">Save Draft</button>
                <button class="btn btn-warning" onclick="exportJSON()">Export JSON</button>
                <button class="btn btn-success" onclick="saveToFile()">Save File</button>
            </div>
        </div>
    </div>

    <div class="nav-bar">
        <a href="index.html">Home</a>
        <a href="final-action-chair-report-full.html">Final Report</a>
        <a href="comparison-enhanced.html">Comparison</a>
        <a href="report-editor.html" class="active">Report Editor</a>
    </div>

    <div class="main-container">
        <div class="sidebar">
            <div class="sidebar-group">General</div>
            <div class="sidebar-section" onclick="showPanel('metadata')">Metadata (Info)</div>
            <div class="sidebar-section active" onclick="showPanel('summary')">Summary</div>
            <div class="sidebar-section" onclick="showPanel('leadership')">Leadership</div>

            <div class="sidebar-group">Content</div>
            <div class="sidebar-section" onclick="showPanel('participants')">Participants ({num_countries})</div>
            <div class="sidebar-section" onclick="showPanel('objectives')">Objectives ({num_objectives})</div>
            <div class="sidebar-section" onclick="showPanel('deliverables')">Deliverables ({num_deliverables})</div>
            <div class="sidebar-section" onclick="showPanel('publications')">Publications ({num_publications})</div>
            <div class="sidebar-section" onclick="showPanel('events')">Events ({num_events})</div>

            <div class="sidebar-group">Additional</div>
            <div class="sidebar-section" onclick="showPanel('stsms')">STSMs & VMGs</div>
            <div class="sidebar-section" onclick="showPanel('impacts')">Impacts</div>

            <div class="sidebar-group">Export</div>
            <div class="sidebar-section" onclick="showPanel('preview')">Preview & Export</div>
        </div>

        <div class="editor-area">
            <!-- Metadata Panel (Display Only) -->
            <div id="panel-metadata" class="editor-panel">
                <h2>Report Metadata (Read-Only)</h2>
                <p style="margin-bottom: 20px; color: var(--cost-gray);">These fields are auto-generated and cannot be edited.</p>

                <div class="meta-display"><strong>Title:</strong> <span id="meta-title">{escape_html(final_data.get('metadata', {}).get('title', 'N/A'))}</span></div>
                <div class="meta-display"><strong>Action Code:</strong> <span id="meta-action-code">{escape_html(final_data.get('metadata', {}).get('action_code', 'N/A'))}</span></div>
                <div class="meta-display"><strong>Action Name:</strong> <span id="meta-action-name">{escape_html(final_data.get('metadata', {}).get('action_name', 'N/A'))}</span></div>
                <div class="meta-display"><strong>Period:</strong> <span id="meta-period">{escape_html(final_data.get('metadata', {}).get('period', 'N/A'))}</span></div>
                <div class="meta-display"><strong>Pages:</strong> <span id="meta-pages">{final_data.get('metadata', {}).get('pages', 'N/A')}</span></div>
                <div class="meta-display"><strong>Generated:</strong> <span id="meta-generated">{escape_html(final_data.get('metadata', {}).get('generated', 'N/A'))}</span></div>
                <div class="meta-display"><strong>Source File:</strong> <span id="meta-source">{escape_html(final_data.get('metadata', {}).get('source_file', 'N/A'))}</span></div>
            </div>

            <!-- Summary Panel -->
            <div id="panel-summary" class="editor-panel active">
                <h2>Summary Information</h2>

                <div class="form-group">
                    <label>Main Objective</label>
                    <textarea id="summary-main-objective" onchange="markModified('summary')">{escape_html(final_data.get('summary', {}).get('main_objective', ''))}</textarea>
                </div>

                <div class="form-group">
                    <label>Description</label>
                    <textarea id="summary-description" class="large" onchange="markModified('summary')">{escape_html(final_data.get('summary', {}).get('description', ''))}</textarea>
                </div>

                <div class="form-group">
                    <label>Website URL</label>
                    <input type="url" id="summary-website" value="{escape_html(final_data.get('summary', {}).get('website', ''))}" onchange="markModified('summary')">
                </div>

                <h3>Statistics</h3>
                <div class="stats-grid">
                    <div class="form-group">
                        <label>Researchers</label>
                        <input type="number" id="stats-researchers" value="{final_data.get('summary', {}).get('stats', {}).get('researchers', 0)}" onchange="markModified('summary')">
                    </div>
                    <div class="form-group">
                        <label>Countries</label>
                        <input type="number" id="stats-countries" value="{final_data.get('summary', {}).get('stats', {}).get('countries', 0)}" onchange="markModified('summary')">
                    </div>
                    <div class="form-group">
                        <label>COST Countries</label>
                        <input type="number" id="stats-cost-countries" value="{final_data.get('summary', {}).get('stats', {}).get('cost_countries', 0)}" onchange="markModified('summary')">
                    </div>
                    <div class="form-group">
                        <label>Event Participants</label>
                        <input type="number" id="stats-participants" value="{final_data.get('summary', {}).get('stats', {}).get('participants', 0)}" onchange="markModified('summary')">
                    </div>
                    <div class="form-group">
                        <label>Citations</label>
                        <input type="number" id="stats-citations" value="{final_data.get('summary', {}).get('stats', {}).get('citations', 0)}" onchange="markModified('summary')">
                    </div>
                </div>
            </div>

            <!-- Leadership Panel -->
            <div id="panel-leadership" class="editor-panel">
                <h2>Leadership</h2>

                <h3>Action Chair</h3>
                <div class="stats-grid">
                    <div class="form-group">
                        <label>Title</label>
                        <input type="text" id="chair-title" value="{escape_html(final_data.get('leadership', {}).get('chair', {}).get('title', ''))}" onchange="markModified('leadership')">
                    </div>
                    <div class="form-group">
                        <label>Name</label>
                        <input type="text" id="chair-name" value="{escape_html(final_data.get('leadership', {}).get('chair', {}).get('name', ''))}" onchange="markModified('leadership')">
                    </div>
                    <div class="form-group">
                        <label>Email</label>
                        <input type="email" id="chair-email" value="{escape_html(final_data.get('leadership', {}).get('chair', {}).get('email', ''))}" onchange="markModified('leadership')">
                    </div>
                    <div class="form-group">
                        <label>Phone</label>
                        <input type="tel" id="chair-phone" value="{escape_html(final_data.get('leadership', {}).get('chair', {}).get('phone', ''))}" onchange="markModified('leadership')">
                    </div>
                    <div class="form-group">
                        <label>Country</label>
                        <input type="text" id="chair-country" value="{escape_html(final_data.get('leadership', {}).get('chair', {}).get('country', ''))}" onchange="markModified('leadership')">
                    </div>
                </div>

                <h3>Vice-Chair</h3>
                <div class="stats-grid">
                    <div class="form-group">
                        <label>Title</label>
                        <input type="text" id="vicechair-title" value="{escape_html(final_data.get('leadership', {}).get('vice_chair', {}).get('title', ''))}" onchange="markModified('leadership')">
                    </div>
                    <div class="form-group">
                        <label>Name</label>
                        <input type="text" id="vicechair-name" value="{escape_html(final_data.get('leadership', {}).get('vice_chair', {}).get('name', ''))}" onchange="markModified('leadership')">
                    </div>
                    <div class="form-group">
                        <label>Email</label>
                        <input type="email" id="vicechair-email" value="{escape_html(final_data.get('leadership', {}).get('vice_chair', {}).get('email', ''))}" onchange="markModified('leadership')">
                    </div>
                    <div class="form-group">
                        <label>Phone</label>
                        <input type="tel" id="vicechair-phone" value="{escape_html(final_data.get('leadership', {}).get('vice_chair', {}).get('phone', ''))}" onchange="markModified('leadership')">
                    </div>
                    <div class="form-group">
                        <label>Country</label>
                        <input type="text" id="vicechair-country" value="{escape_html(final_data.get('leadership', {}).get('vice_chair', {}).get('country', ''))}" onchange="markModified('leadership')">
                    </div>
                </div>

                <h3>Working Group Leaders</h3>
                <div id="wg-leaders-container"></div>

                <h3>Other Leadership Positions</h3>
                <div id="other-positions-container"></div>
            </div>

            <!-- Participants Panel -->
            <div id="panel-participants" class="editor-panel">
                <h2>Participating Countries ({num_countries})</h2>
                <p style="margin-bottom: 20px; color: var(--cost-gray);">Countries that have joined the COST Action with their joining dates.</p>

                <div id="countries-container"></div>
                <button class="add-btn" onclick="addCountry()">+ Add Country</button>
            </div>

            <!-- Objectives Panel -->
            <div id="panel-objectives" class="editor-panel">
                <h2>MoU Objectives ({num_objectives})</h2>
                <p style="margin-bottom: 20px; color: var(--cost-gray);">Click on an objective to expand and edit its details.</p>

                <div id="objectives-container"></div>
            </div>

            <!-- Deliverables Panel -->
            <div id="panel-deliverables" class="editor-panel">
                <h2>Deliverables ({num_deliverables})</h2>
                <p style="margin-bottom: 20px; color: var(--cost-gray);">Edit deliverable status, details, and proof URLs.</p>

                <div id="deliverables-container"></div>
            </div>

            <!-- Publications Panel -->
            <div id="panel-publications" class="editor-panel">
                <h2>Publications ({num_publications})</h2>
                <p style="margin-bottom: 20px; color: var(--cost-gray);">Edit DOIs for all publications. Title shown for reference.</p>

                <div id="publications-container" style="max-height: 700px; overflow-y: auto;"></div>
                <button class="add-btn" onclick="addPublication()">+ Add Publication</button>
            </div>

            <!-- Events Panel -->
            <div id="panel-events" class="editor-panel">
                <h2>Events ({num_events})</h2>
                <p style="margin-bottom: 20px; color: var(--cost-gray);">Event URLs and links.</p>

                <div id="events-container"></div>
                <button class="add-btn" onclick="addEvent()">+ Add Event</button>
            </div>

            <!-- STSMs Panel -->
            <div id="panel-stsms" class="editor-panel">
                <h2>STSMs & Virtual Mobility Grants</h2>

                <h3>Short-Term Scientific Missions</h3>
                <div class="form-group">
                    <label>STSMs Description</label>
                    <textarea id="stsms-description" class="large" onchange="markModified('stsms')"></textarea>
                </div>

                <h3>Virtual Mobility Grants</h3>
                <div id="vmgs-container"></div>
                <button class="add-btn" onclick="addVMG()">+ Add VMG</button>
            </div>

            <!-- Impacts Panel -->
            <div id="panel-impacts" class="editor-panel">
                <h2>Career Impacts & Achievements</h2>

                <div class="form-group">
                    <label>Career Benefits</label>
                    <textarea id="impacts-career" class="large" onchange="markModified('impacts')">{escape_html(final_data.get('impacts', {}).get('career_benefits', ''))}</textarea>
                </div>

                <div class="form-group">
                    <label>Experience Level</label>
                    <select id="impacts-experience" onchange="markModified('impacts')">
                        <option value="">Select...</option>
                        <option value="Early Career Investigators">Early Career Investigators</option>
                        <option value="Mid-Career Researchers">Mid-Career Researchers</option>
                        <option value="Senior Researchers">Senior Researchers</option>
                        <option value="All Levels">All Levels</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>Stakeholder Engagement</label>
                    <textarea id="impacts-stakeholder" class="large" onchange="markModified('impacts')">{escape_html(final_data.get('impacts', {}).get('stakeholder_engagement', ''))}</textarea>
                </div>

                <div class="form-group">
                    <label>Dissemination Approach</label>
                    <textarea id="impacts-dissemination" class="large" onchange="markModified('impacts')">{escape_html(final_data.get('impacts', {}).get('dissemination_approach', ''))}</textarea>
                </div>
            </div>

            <!-- Preview Panel -->
            <div id="panel-preview" class="editor-panel">
                <h2>Preview & Export</h2>

                <div style="margin-bottom: 20px;">
                    <button class="btn btn-primary" onclick="generatePreview()">Generate Preview</button>
                    <button class="btn btn-success" onclick="exportJSON()">Export as JSON</button>
                    <button class="btn btn-warning" onclick="exportTXT()">Export as TXT</button>
                </div>

                <div class="form-group">
                    <label>JSON Preview</label>
                    <textarea id="json-preview" class="large" style="min-height: 500px; font-family: monospace; font-size: 0.9em;" readonly></textarea>
                </div>
            </div>
        </div>
    </div>

    <div class="status-bar">
        <div class="status-indicator">
            <span class="status-dot saved" id="status-dot"></span>
            <span id="status-text">All changes saved</span>
        </div>
        <div>
            <span id="last-saved">Last saved: Never</span>
        </div>
    </div>

    <div id="toast" class="toast"></div>

    <script>
        // Initialize report data
        let reportData = {report_json};
        let originalData = JSON.parse(JSON.stringify(reportData));
        let modifiedSections = new Set();

        // Load from localStorage if available
        const savedData = localStorage.getItem('cost_report_draft');
        if (savedData) {{
            try {{
                reportData = JSON.parse(savedData);
                showToast('Draft loaded from local storage', 'info');
            }} catch (e) {{
                console.error('Error loading draft:', e);
            }}
        }}

        // Initialize UI
        document.addEventListener('DOMContentLoaded', function() {{
            renderObjectives();
            renderDeliverables();
            renderPublications();
            renderWGLeaders();
            renderOtherPositions();
            renderCountries();
            renderEvents();
            renderSTSMs();
            renderVMGs();
            updateLastSaved();
        }});

        // Panel switching
        function showPanel(panelId) {{
            document.querySelectorAll('.editor-panel').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.sidebar-section').forEach(s => s.classList.remove('active'));

            document.getElementById('panel-' + panelId).classList.add('active');
            event.target.classList.add('active');
        }}

        // Mark section as modified
        function markModified(section) {{
            modifiedSections.add(section);
            document.getElementById('status-dot').className = 'status-dot modified';
            document.getElementById('status-text').textContent = 'Unsaved changes';

            // Auto-save to localStorage after 2 seconds
            clearTimeout(window.autoSaveTimeout);
            window.autoSaveTimeout = setTimeout(() => {{
                collectAllData();
                localStorage.setItem('cost_report_draft', JSON.stringify(reportData));
            }}, 2000);
        }}

        // Render functions
        function renderObjectives() {{
            const container = document.getElementById('objectives-container');
            container.innerHTML = '';

            reportData.objectives.forEach((obj, index) => {{
                const typeStr = Array.isArray(obj.type) ? obj.type.join(', ') : (obj.type || '');
                container.innerHTML += `
                    <div class="objective-editor">
                        <div class="objective-header" onclick="toggleObjective(${{index}})">
                            <span>Objective ${{obj.number}}: ${{(obj.title || '').substring(0, 70)}}...</span>
                            <span>[${{obj.achievement || 'N/A'}}]</span>
                        </div>
                        <div id="obj-body-${{index}}" class="objective-body">
                            <div class="form-group">
                                <label>Title</label>
                                <textarea id="obj-title-${{index}}" onchange="markModified('objectives')">${{obj.title || ''}}</textarea>
                            </div>
                            <div class="stats-grid">
                                <div class="form-group">
                                    <label>Type (COST codes, comma-separated)</label>
                                    <input type="text" id="obj-type-${{index}}" value="${{typeStr}}" onchange="markModified('objectives')">
                                </div>
                                <div class="form-group">
                                    <label>Achievement Level</label>
                                    <select id="obj-achievement-${{index}}" onchange="markModified('objectives')">
                                        <option value="76-100%" ${{obj.achievement === '76-100%' ? 'selected' : ''}}>76-100%</option>
                                        <option value="51-75%" ${{obj.achievement === '51-75%' ? 'selected' : ''}}>51-75%</option>
                                        <option value="26-50%" ${{obj.achievement === '26-50%' ? 'selected' : ''}}>26-50%</option>
                                        <option value="0-25%" ${{obj.achievement === '0-25%' ? 'selected' : ''}}>0-25%</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label>Dependence on Networking</label>
                                    <select id="obj-dependence-${{index}}" onchange="markModified('objectives')">
                                        <option value="Strong" ${{obj.dependence === 'Strong' ? 'selected' : ''}}>Strong</option>
                                        <option value="High" ${{obj.dependence === 'High' ? 'selected' : ''}}>High</option>
                                        <option value="Medium" ${{obj.dependence === 'Medium' ? 'selected' : ''}}>Medium</option>
                                        <option value="Weak" ${{obj.dependence === 'Weak' ? 'selected' : ''}}>Weak</option>
                                    </select>
                                </div>
                            </div>
                            <div class="form-group">
                                <label>Proof Text</label>
                                <textarea id="obj-proof-${{index}}" class="large" onchange="markModified('objectives')">${{obj.proof_text || ''}}</textarea>
                            </div>
                        </div>
                    </div>
                `;
            }});
        }}

        function toggleObjective(index) {{
            document.getElementById('obj-body-' + index).classList.toggle('expanded');
        }}

        function renderDeliverables() {{
            const container = document.getElementById('deliverables-container');
            container.innerHTML = '';

            reportData.deliverables.forEach((del, index) => {{
                container.innerHTML += `
                    <div class="data-row deliverable-row">
                        <strong>D${{del.number}}</strong>
                        <input type="text" id="del-title-${{index}}" value="${{del.title || ''}}" onchange="markModified('deliverables')" placeholder="Title">
                        <select id="del-status-${{index}}" onchange="markModified('deliverables')">
                            <option value="Delivered" ${{del.status === 'Delivered' ? 'selected' : ''}}>Delivered</option>
                            <option value="Not delivered" ${{del.status !== 'Delivered' ? 'selected' : ''}}>Not delivered</option>
                        </select>
                        <select id="del-dependence-${{index}}" onchange="markModified('deliverables')">
                            <option value="Strong" ${{del.dependence === 'Strong' ? 'selected' : ''}}>Strong</option>
                            <option value="High" ${{del.dependence === 'High' ? 'selected' : ''}}>High</option>
                            <option value="Medium" ${{del.dependence === 'Medium' ? 'selected' : ''}}>Medium</option>
                            <option value="Weak" ${{del.dependence === 'Weak' ? 'selected' : ''}}>Weak</option>
                        </select>
                        <input type="url" id="del-proof-${{index}}" value="${{del.proof_url || ''}}" onchange="markModified('deliverables')" placeholder="Proof URL">
                    </div>
                `;
            }});
        }}

        function renderPublications() {{
            const container = document.getElementById('publications-container');
            container.innerHTML = '';

            reportData.publications.forEach((pub, index) => {{
                container.innerHTML += `
                    <div class="data-row publication-row">
                        <strong>#${{pub.number || index + 1}}</strong>
                        <div style="flex: 1;">
                            <div style="font-size: 0.9em; color: var(--cost-gray); margin-bottom: 5px;">${{(pub.title || 'Untitled').substring(0, 100)}}...</div>
                            <input type="text" id="pub-doi-${{index}}" value="${{pub.doi || ''}}" onchange="markModified('publications')" placeholder="doi:10.xxxx/yyyy" style="width: 100%;">
                        </div>
                    </div>
                `;
            }});
        }}

        function renderWGLeaders() {{
            const container = document.getElementById('wg-leaders-container');
            container.innerHTML = '';

            const wgLeaders = reportData.leadership?.wg_leaders || [];
            wgLeaders.forEach((wg, index) => {{
                container.innerHTML += `
                    <div style="background: var(--bg-light); padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                        <strong style="color: var(--cost-purple);">WG${{wg.wg_number}}: ${{(wg.wg_title || '').substring(0, 50)}}...</strong>
                        <div class="stats-grid" style="margin-top: 10px;">
                            <div class="form-group">
                                <label>Leader Name</label>
                                <input type="text" id="wg-name-${{index}}" value="${{wg.name || ''}}" onchange="markModified('leadership')">
                            </div>
                            <div class="form-group">
                                <label>Email</label>
                                <input type="email" id="wg-email-${{index}}" value="${{wg.email || ''}}" onchange="markModified('leadership')">
                            </div>
                            <div class="form-group">
                                <label>Country</label>
                                <input type="text" id="wg-country-${{index}}" value="${{wg.country || ''}}" onchange="markModified('leadership')">
                            </div>
                            <div class="form-group">
                                <label>Participants</label>
                                <input type="number" id="wg-participants-${{index}}" value="${{wg.participants || 0}}" onchange="markModified('leadership')">
                            </div>
                        </div>
                    </div>
                `;
            }});
        }}

        function renderOtherPositions() {{
            const container = document.getElementById('other-positions-container');
            container.innerHTML = '';

            const otherPos = reportData.leadership?.other_positions || [];
            otherPos.forEach((pos, index) => {{
                container.innerHTML += `
                    <div class="data-row other-pos-row">
                        <input type="text" id="otherpos-position-${{index}}" value="${{pos.position || ''}}" onchange="markModified('leadership')" placeholder="Position">
                        <input type="text" id="otherpos-name-${{index}}" value="${{pos.name || ''}}" onchange="markModified('leadership')" placeholder="Name">
                        <input type="email" id="otherpos-email-${{index}}" value="${{pos.email || ''}}" onchange="markModified('leadership')" placeholder="Email">
                        <input type="text" id="otherpos-country-${{index}}" value="${{pos.country || ''}}" onchange="markModified('leadership')" placeholder="Country">
                    </div>
                `;
            }});

            if (otherPos.length === 0) {{
                container.innerHTML = '<p style="color: var(--cost-gray);">No other positions defined.</p>';
            }}
        }}

        function renderCountries() {{
            const container = document.getElementById('countries-container');
            container.innerHTML = '';

            const countries = reportData.participants?.countries || [];
            countries.forEach((c, index) => {{
                container.innerHTML += `
                    <div class="data-row country-row">
                        <input type="text" id="country-code-${{index}}" value="${{c.code || ''}}" onchange="markModified('participants')" placeholder="XX" maxlength="2" style="text-transform: uppercase;">
                        <input type="text" id="country-date-${{index}}" value="${{c.date || ''}}" onchange="markModified('participants')" placeholder="DD/MM/YYYY">
                        <button class="delete-btn" onclick="deleteCountry(${{index}})">X</button>
                    </div>
                `;
            }});
        }}

        function renderEvents() {{
            const container = document.getElementById('events-container');
            container.innerHTML = '';

            const events = reportData.events || [];
            events.forEach((evt, index) => {{
                container.innerHTML += `
                    <div class="data-row event-row">
                        <strong>#${{index + 1}}</strong>
                        <input type="url" id="event-url-${{index}}" value="${{evt.url || ''}}" onchange="markModified('events')" placeholder="Event URL">
                        <button class="delete-btn" onclick="deleteEvent(${{index}})">X</button>
                    </div>
                `;
            }});

            if (events.length === 0) {{
                container.innerHTML = '<p style="color: var(--cost-gray);">No events defined.</p>';
            }}
        }}

        function renderSTSMs() {{
            const stsms = reportData.stsms_vmgs?.stsms || [];
            if (stsms.length > 0 && stsms[0].description) {{
                document.getElementById('stsms-description').value = stsms[0].description;
            }}
        }}

        function renderVMGs() {{
            const container = document.getElementById('vmgs-container');
            container.innerHTML = '';

            const vmgs = reportData.stsms_vmgs?.vmgs || [];
            vmgs.forEach((vmg, index) => {{
                container.innerHTML += `
                    <div class="data-row" style="grid-template-columns: 1fr 40px;">
                        <input type="text" id="vmg-desc-${{index}}" value="${{vmg.description || ''}}" onchange="markModified('stsms')" placeholder="VMG Description">
                        <button class="delete-btn" onclick="deleteVMG(${{index}})">X</button>
                    </div>
                `;
            }});

            if (vmgs.length === 0) {{
                container.innerHTML = '<p style="color: var(--cost-gray);">No VMGs defined.</p>';
            }}
        }}

        // Add/Delete functions
        function addCountry() {{
            if (!reportData.participants) reportData.participants = {{ countries: [] }};
            if (!reportData.participants.countries) reportData.participants.countries = [];
            reportData.participants.countries.push({{ code: '', date: '' }});
            renderCountries();
            markModified('participants');
        }}

        function deleteCountry(index) {{
            reportData.participants.countries.splice(index, 1);
            renderCountries();
            markModified('participants');
        }}

        function addEvent() {{
            if (!reportData.events) reportData.events = [];
            reportData.events.push({{ url: '' }});
            renderEvents();
            markModified('events');
        }}

        function deleteEvent(index) {{
            reportData.events.splice(index, 1);
            renderEvents();
            markModified('events');
        }}

        function addPublication() {{
            reportData.publications.push({{
                number: reportData.publications.length + 1,
                title: '',
                authors: '',
                doi: '',
                type: '',
                published_in: '',
                countries: []
            }});
            renderPublications();
            markModified('publications');
        }}

        function addVMG() {{
            if (!reportData.stsms_vmgs) reportData.stsms_vmgs = {{ stsms: [], vmgs: [] }};
            if (!reportData.stsms_vmgs.vmgs) reportData.stsms_vmgs.vmgs = [];
            reportData.stsms_vmgs.vmgs.push({{ description: '' }});
            renderVMGs();
            markModified('stsms');
        }}

        function deleteVMG(index) {{
            reportData.stsms_vmgs.vmgs.splice(index, 1);
            renderVMGs();
            markModified('stsms');
        }}

        // Collect all data from form
        function collectAllData() {{
            // Summary
            reportData.summary = reportData.summary || {{}};
            reportData.summary.main_objective = document.getElementById('summary-main-objective')?.value || '';
            reportData.summary.description = document.getElementById('summary-description')?.value || '';
            reportData.summary.website = document.getElementById('summary-website')?.value || '';
            reportData.summary.stats = {{
                researchers: parseInt(document.getElementById('stats-researchers')?.value) || 0,
                countries: parseInt(document.getElementById('stats-countries')?.value) || 0,
                cost_countries: parseInt(document.getElementById('stats-cost-countries')?.value) || 0,
                participants: parseInt(document.getElementById('stats-participants')?.value) || 0,
                citations: parseInt(document.getElementById('stats-citations')?.value) || 0
            }};

            // Leadership
            reportData.leadership = reportData.leadership || {{}};
            reportData.leadership.chair = {{
                title: document.getElementById('chair-title')?.value || '',
                name: document.getElementById('chair-name')?.value || '',
                email: document.getElementById('chair-email')?.value || '',
                phone: document.getElementById('chair-phone')?.value || '',
                country: document.getElementById('chair-country')?.value || ''
            }};
            reportData.leadership.vice_chair = {{
                title: document.getElementById('vicechair-title')?.value || '',
                name: document.getElementById('vicechair-name')?.value || '',
                email: document.getElementById('vicechair-email')?.value || '',
                phone: document.getElementById('vicechair-phone')?.value || '',
                country: document.getElementById('vicechair-country')?.value || ''
            }};

            // WG Leaders
            (reportData.leadership.wg_leaders || []).forEach((wg, index) => {{
                wg.name = document.getElementById('wg-name-' + index)?.value || '';
                wg.email = document.getElementById('wg-email-' + index)?.value || '';
                wg.country = document.getElementById('wg-country-' + index)?.value || '';
                wg.participants = parseInt(document.getElementById('wg-participants-' + index)?.value) || 0;
            }});

            // Other Positions
            (reportData.leadership.other_positions || []).forEach((pos, index) => {{
                pos.position = document.getElementById('otherpos-position-' + index)?.value || '';
                pos.name = document.getElementById('otherpos-name-' + index)?.value || '';
                pos.email = document.getElementById('otherpos-email-' + index)?.value || '';
                pos.country = document.getElementById('otherpos-country-' + index)?.value || '';
            }});

            // Participants/Countries
            (reportData.participants?.countries || []).forEach((c, index) => {{
                c.code = document.getElementById('country-code-' + index)?.value?.toUpperCase() || '';
                c.date = document.getElementById('country-date-' + index)?.value || '';
            }});

            // Objectives
            reportData.objectives.forEach((obj, index) => {{
                obj.title = document.getElementById('obj-title-' + index)?.value || '';
                const typeVal = document.getElementById('obj-type-' + index)?.value || '';
                obj.type = typeVal ? typeVal.split(',').map(t => t.trim()) : [];
                obj.achievement = document.getElementById('obj-achievement-' + index)?.value || '';
                obj.dependence = document.getElementById('obj-dependence-' + index)?.value || '';
                obj.proof_text = document.getElementById('obj-proof-' + index)?.value || '';
            }});

            // Deliverables
            reportData.deliverables.forEach((del, index) => {{
                del.title = document.getElementById('del-title-' + index)?.value || '';
                del.status = document.getElementById('del-status-' + index)?.value || '';
                del.dependence = document.getElementById('del-dependence-' + index)?.value || '';
                del.proof_url = document.getElementById('del-proof-' + index)?.value || '';
            }});

            // Publications (DOI only)
            reportData.publications.forEach((pub, index) => {{
                pub.doi = document.getElementById('pub-doi-' + index)?.value || '';
            }});

            // Events
            (reportData.events || []).forEach((evt, index) => {{
                evt.url = document.getElementById('event-url-' + index)?.value || '';
            }});

            // STSMs
            reportData.stsms_vmgs = reportData.stsms_vmgs || {{ stsms: [], vmgs: [] }};
            if (!reportData.stsms_vmgs.stsms) reportData.stsms_vmgs.stsms = [];
            if (reportData.stsms_vmgs.stsms.length === 0) {{
                reportData.stsms_vmgs.stsms.push({{ description: '', key_activities: [] }});
            }}
            reportData.stsms_vmgs.stsms[0].description = document.getElementById('stsms-description')?.value || '';

            // VMGs
            (reportData.stsms_vmgs.vmgs || []).forEach((vmg, index) => {{
                vmg.description = document.getElementById('vmg-desc-' + index)?.value || '';
            }});

            // Impacts
            reportData.impacts = reportData.impacts || {{}};
            reportData.impacts.career_benefits = document.getElementById('impacts-career')?.value || '';
            reportData.impacts.experience_level = document.getElementById('impacts-experience')?.value || '';
            reportData.impacts.stakeholder_engagement = document.getElementById('impacts-stakeholder')?.value || '';
            reportData.impacts.dissemination_approach = document.getElementById('impacts-dissemination')?.value || '';

            return reportData;
        }}

        // Save functions
        function saveToLocalStorage() {{
            collectAllData();
            localStorage.setItem('cost_report_draft', JSON.stringify(reportData));
            updateSaveStatus('saved');
            showToast('Draft saved to local storage', 'success');
            updateLastSaved();
        }}

        async function saveToFile() {{
            collectAllData();

            if ('showSaveFilePicker' in window) {{
                try {{
                    const handle = await window.showSaveFilePicker({{
                        suggestedName: 'final_report_full.json',
                        types: [{{ description: 'JSON files', accept: {{ 'application/json': ['.json'] }} }}]
                    }});
                    const writable = await handle.createWritable();
                    await writable.write(JSON.stringify(reportData, null, 2));
                    await writable.close();
                    updateSaveStatus('saved');
                    showToast('File saved successfully!', 'success');
                    updateLastSaved();
                }} catch (err) {{
                    if (err.name !== 'AbortError') showToast('Error: ' + err.message, 'error');
                }}
            }} else {{
                exportJSON();
            }}
        }}

        function exportJSON() {{
            collectAllData();
            const blob = new Blob([JSON.stringify(reportData, null, 2)], {{ type: 'application/json' }});
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = 'final_report_full_' + new Date().toISOString().slice(0,10) + '.json';
            a.click();
            showToast('JSON exported!', 'success');
        }}

        function exportTXT() {{
            collectAllData();
            let txt = 'COST Action CA19130 - Final Achievement Report\\n';
            txt += '='.repeat(60) + '\\n\\n';
            txt += 'SUMMARY\\n' + '-'.repeat(40) + '\\n';
            txt += reportData.summary.main_objective + '\\n\\n';
            txt += reportData.summary.description + '\\n\\n';
            txt += 'OBJECTIVES\\n' + '-'.repeat(40) + '\\n';
            reportData.objectives.forEach(obj => {{
                txt += `\\nObjective ${{obj.number}}: ${{obj.title}}\\n`;
                txt += `Achievement: ${{obj.achievement}}\\nProof: ${{obj.proof_text}}\\n`;
            }});
            const blob = new Blob([txt], {{ type: 'text/plain' }});
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = 'final_report_' + new Date().toISOString().slice(0,10) + '.txt';
            a.click();
            showToast('TXT exported!', 'success');
        }}

        async function loadFromFile() {{
            if ('showOpenFilePicker' in window) {{
                try {{
                    const [handle] = await window.showOpenFilePicker({{
                        types: [{{ description: 'JSON files', accept: {{ 'application/json': ['.json'] }} }}]
                    }});
                    const file = await handle.getFile();
                    reportData = JSON.parse(await file.text());
                    renderAll();
                    showToast('File loaded!', 'success');
                }} catch (err) {{
                    if (err.name !== 'AbortError') showToast('Error: ' + err.message, 'error');
                }}
            }} else {{
                showToast('File System API not supported', 'info');
            }}
        }}

        function resetToOriginal() {{
            if (confirm('Reset all changes? This cannot be undone.')) {{
                reportData = JSON.parse(JSON.stringify(originalData));
                localStorage.removeItem('cost_report_draft');
                renderAll();
                updateSaveStatus('saved');
                showToast('Reset to original', 'info');
            }}
        }}

        function renderAll() {{
            renderObjectives();
            renderDeliverables();
            renderPublications();
            renderWGLeaders();
            renderOtherPositions();
            renderCountries();
            renderEvents();
            renderSTSMs();
            renderVMGs();
        }}

        function generatePreview() {{
            collectAllData();
            document.getElementById('json-preview').value = JSON.stringify(reportData, null, 2);
        }}

        function updateSaveStatus(status) {{
            const dot = document.getElementById('status-dot');
            const text = document.getElementById('status-text');
            if (status === 'saved') {{
                dot.className = 'status-dot saved';
                text.textContent = 'All changes saved';
                modifiedSections.clear();
            }}
        }}

        function updateLastSaved() {{
            document.getElementById('last-saved').textContent = 'Last saved: ' + new Date().toLocaleString();
        }}

        function showToast(message, type) {{
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.className = 'toast ' + type + ' show';
            setTimeout(() => toast.classList.remove('show'), 3000);
        }}

        // Keyboard shortcuts
        document.addEventListener('keydown', e => {{
            if (e.ctrlKey && e.key === 's') {{
                e.preventDefault();
                saveToLocalStorage();
            }}
        }});
    </script>
</body>
</html>
"""

    return html


def main():
    """Main function to generate report editor HTML."""
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / "data"

    print("=" * 60)
    print("Generating Report Editor (Full Coverage)")
    print("=" * 60)

    # Load final report data
    print("\nLoading JSON data...")
    with open(data_dir / "final_report_full.json", 'r', encoding='utf-8') as f:
        final_data = json.load(f)

    # Generate HTML
    print("Generating report editor HTML...")
    html = generate_report_editor_html(final_data)

    output_path = base_dir / "report-editor.html"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"\nSaved: {output_path}")
    print(f"Size: {len(html):,} characters")
    print("\n" + "=" * 60)
    print("Done!")


if __name__ == "__main__":
    main()
