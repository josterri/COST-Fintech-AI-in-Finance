"""
Generate an interactive Report Editor HTML page.
Allows editing of all report sections with local save functionality.
"""

import json
from pathlib import Path
from datetime import datetime


def generate_report_editor_html(final_data):
    """Generate an interactive report editor HTML page."""

    # Prepare data for JavaScript
    report_json = json.dumps(final_data, indent=2)

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

        .btn-primary {{
            background: white;
            color: var(--cost-purple);
        }}

        .btn-primary:hover {{
            background: var(--bg-light);
            transform: translateY(-1px);
        }}

        .btn-success {{
            background: var(--cost-green);
            color: white;
        }}

        .btn-success:hover {{
            background: #218838;
        }}

        .btn-warning {{
            background: var(--cost-orange);
            color: white;
        }}

        .btn-danger {{
            background: var(--cost-red);
            color: white;
        }}

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

        .nav-bar a:hover, .nav-bar a.active {{
            background: var(--cost-purple);
            color: white;
        }}

        .main-container {{
            display: flex;
            max-width: 1800px;
            margin: 0 auto;
            min-height: calc(100vh - 150px);
        }}

        /* Sidebar */
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

        .sidebar-section:hover {{
            background: var(--bg-light);
            border-left-color: var(--cost-purple-light);
        }}

        .sidebar-section.active {{
            background: #f0e6f6;
            border-left-color: var(--cost-purple);
            font-weight: 500;
        }}

        .sidebar-section.modified::after {{
            content: '*';
            color: var(--cost-orange);
            margin-left: 5px;
            font-weight: bold;
        }}

        .sidebar-group {{
            font-size: 0.8em;
            text-transform: uppercase;
            color: var(--cost-gray);
            padding: 15px 20px 8px;
            letter-spacing: 1px;
        }}

        /* Editor Area */
        .editor-area {{
            flex: 1;
            padding: 30px 40px;
        }}

        .editor-panel {{
            display: none;
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}

        .editor-panel.active {{
            display: block;
        }}

        .editor-panel h2 {{
            color: var(--cost-purple);
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid var(--bg-light);
        }}

        .form-group {{
            margin-bottom: 25px;
        }}

        .form-group label {{
            display: block;
            font-weight: 500;
            margin-bottom: 8px;
            color: #555;
        }}

        .form-group input,
        .form-group select {{
            width: 100%;
            padding: 12px 15px;
            border: 2px solid var(--border-color);
            border-radius: 8px;
            font-size: 1em;
            transition: border-color 0.2s;
        }}

        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {{
            outline: none;
            border-color: var(--cost-purple);
        }}

        .form-group textarea {{
            width: 100%;
            padding: 15px;
            border: 2px solid var(--border-color);
            border-radius: 8px;
            font-size: 1em;
            font-family: inherit;
            resize: vertical;
            min-height: 150px;
            line-height: 1.7;
        }}

        .form-group textarea.large {{
            min-height: 300px;
        }}

        .form-help {{
            font-size: 0.85em;
            color: var(--cost-gray);
            margin-top: 5px;
        }}

        /* Objectives List */
        .objective-editor {{
            border: 1px solid var(--border-color);
            border-radius: 8px;
            margin-bottom: 15px;
            overflow: hidden;
        }}

        .objective-header {{
            background: var(--cost-purple);
            color: white;
            padding: 12px 20px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .objective-header:hover {{
            background: var(--cost-purple-light);
        }}

        .objective-body {{
            padding: 20px;
            display: none;
            background: #fafafa;
        }}

        .objective-body.expanded {{
            display: block;
        }}

        /* Status Indicators */
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

        .status-indicator {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .status-dot {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
        }}

        .status-dot.saved {{ background: var(--cost-green); }}
        .status-dot.modified {{ background: var(--cost-orange); }}
        .status-dot.error {{ background: var(--cost-red); }}

        /* Toast Notifications */
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

        /* Grid for stats */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}

        .stats-grid .form-group {{
            margin-bottom: 0;
        }}

        /* Publications list */
        .publication-item {{
            background: var(--bg-light);
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
        }}

        .publication-item .pub-num {{
            font-weight: bold;
            color: var(--cost-purple);
        }}

        /* Add button */
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
        }}

        .add-btn:hover {{
            border-color: var(--cost-purple);
            color: var(--cost-purple);
        }}

        /* Deliverable row */
        .deliverable-row {{
            display: grid;
            grid-template-columns: 50px 1fr 150px 150px;
            gap: 15px;
            padding: 15px;
            background: var(--bg-light);
            border-radius: 8px;
            margin-bottom: 10px;
            align-items: center;
        }}

        .deliverable-row input,
        .deliverable-row select {{
            padding: 8px 12px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <div>
                <h1>COST CA19130 Report Editor</h1>
                <div class="subtitle">Edit and save the Final Achievement Report</div>
            </div>
            <div class="header-actions">
                <button class="btn btn-primary" onclick="resetToOriginal()">Reset to Original</button>
                <button class="btn btn-primary" onclick="loadFromFile()">Load from File</button>
                <button class="btn btn-success" onclick="saveToLocalStorage()">Save Draft</button>
                <button class="btn btn-warning" onclick="exportJSON()">Export JSON</button>
                <button class="btn btn-success" onclick="saveToFile()">Save to File</button>
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
            <div class="sidebar-section active" onclick="showPanel('summary')">Summary</div>
            <div class="sidebar-section" onclick="showPanel('leadership')">Leadership</div>

            <div class="sidebar-group">Content</div>
            <div class="sidebar-section" onclick="showPanel('objectives')">Objectives (16)</div>
            <div class="sidebar-section" onclick="showPanel('deliverables')">Deliverables (15)</div>
            <div class="sidebar-section" onclick="showPanel('publications')">Publications</div>

            <div class="sidebar-group">Additional</div>
            <div class="sidebar-section" onclick="showPanel('stsms')">STSMs & VMGs</div>
            <div class="sidebar-section" onclick="showPanel('impacts')">Impacts</div>

            <div class="sidebar-group">Export</div>
            <div class="sidebar-section" onclick="showPanel('preview')">Preview & Export</div>
        </div>

        <div class="editor-area">
            <!-- Summary Panel -->
            <div id="panel-summary" class="editor-panel active">
                <h2>Summary Information</h2>

                <div class="form-group">
                    <label>Main Objective</label>
                    <textarea id="summary-main-objective" onchange="markModified('summary')">{final_data.get('summary', {}).get('main_objective', '')}</textarea>
                </div>

                <div class="form-group">
                    <label>Description</label>
                    <textarea id="summary-description" class="large" onchange="markModified('summary')">{final_data.get('summary', {}).get('description', '')}</textarea>
                </div>

                <div class="form-group">
                    <label>Website URL</label>
                    <input type="url" id="summary-website" value="{final_data.get('summary', {}).get('website', '')}" onchange="markModified('summary')">
                </div>

                <h3 style="margin: 30px 0 20px; color: var(--cost-purple);">Statistics</h3>
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
                        <label>Conferences</label>
                        <input type="number" id="stats-conferences" value="{final_data.get('summary', {}).get('stats', {}).get('conferences', 0)}" onchange="markModified('summary')">
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

                <h3 style="margin: 20px 0 15px; color: var(--cost-purple);">Action Chair</h3>
                <div class="stats-grid">
                    <div class="form-group">
                        <label>Name</label>
                        <input type="text" id="chair-name" value="{final_data.get('leadership', {}).get('chair', {}).get('name', '')}" onchange="markModified('leadership')">
                    </div>
                    <div class="form-group">
                        <label>Email</label>
                        <input type="email" id="chair-email" value="{final_data.get('leadership', {}).get('chair', {}).get('email', '')}" onchange="markModified('leadership')">
                    </div>
                    <div class="form-group">
                        <label>Country</label>
                        <input type="text" id="chair-country" value="{final_data.get('leadership', {}).get('chair', {}).get('country', '')}" onchange="markModified('leadership')">
                    </div>
                </div>

                <h3 style="margin: 30px 0 15px; color: var(--cost-purple);">Vice-Chair</h3>
                <div class="stats-grid">
                    <div class="form-group">
                        <label>Name</label>
                        <input type="text" id="vicechair-name" value="{final_data.get('leadership', {}).get('vice_chair', {}).get('name', '')}" onchange="markModified('leadership')">
                    </div>
                    <div class="form-group">
                        <label>Email</label>
                        <input type="email" id="vicechair-email" value="{final_data.get('leadership', {}).get('vice_chair', {}).get('email', '')}" onchange="markModified('leadership')">
                    </div>
                    <div class="form-group">
                        <label>Country</label>
                        <input type="text" id="vicechair-country" value="{final_data.get('leadership', {}).get('vice_chair', {}).get('country', '')}" onchange="markModified('leadership')">
                    </div>
                </div>

                <h3 style="margin: 30px 0 15px; color: var(--cost-purple);">Working Group Leaders</h3>
                <div id="wg-leaders-container"></div>
            </div>

            <!-- Objectives Panel -->
            <div id="panel-objectives" class="editor-panel">
                <h2>MoU Objectives</h2>
                <p style="margin-bottom: 20px; color: var(--cost-gray);">Click on an objective to expand and edit its details.</p>

                <div id="objectives-container"></div>
            </div>

            <!-- Deliverables Panel -->
            <div id="panel-deliverables" class="editor-panel">
                <h2>Deliverables</h2>
                <p style="margin-bottom: 20px; color: var(--cost-gray);">Edit deliverable status and details.</p>

                <div id="deliverables-container"></div>
            </div>

            <!-- Publications Panel -->
            <div id="panel-publications" class="editor-panel">
                <h2>Publications</h2>
                <p style="margin-bottom: 20px; color: var(--cost-gray);">Manage co-authored publications.</p>

                <div class="form-group">
                    <label>Total Publications</label>
                    <input type="number" id="pub-count" value="{len(final_data.get('publications', []))}" readonly>
                </div>

                <div id="publications-container" style="max-height: 600px; overflow-y: auto;"></div>

                <button class="add-btn" onclick="addPublication()" style="margin-top: 15px;">+ Add Publication</button>
            </div>

            <!-- STSMs Panel -->
            <div id="panel-stsms" class="editor-panel">
                <h2>STSMs & Virtual Mobility Grants</h2>

                <div class="form-group">
                    <label>STSMs Description</label>
                    <textarea id="stsms-description" class="large" onchange="markModified('stsms')"></textarea>
                </div>

                <h3 style="margin: 30px 0 15px; color: var(--cost-purple);">Virtual Mobility Grants</h3>
                <div id="vmgs-container"></div>
            </div>

            <!-- Impacts Panel -->
            <div id="panel-impacts" class="editor-panel">
                <h2>Career Impacts & Achievements</h2>

                <div class="form-group">
                    <label>Career Benefits</label>
                    <textarea id="impacts-career" class="large" onchange="markModified('impacts')">{final_data.get('impacts', {}).get('career_benefits', '')}</textarea>
                </div>

                <div class="form-group">
                    <label>Experience Level</label>
                    <select id="impacts-experience" onchange="markModified('impacts')">
                        <option value="Early Career Investigators">Early Career Investigators</option>
                        <option value="Mid-Career Researchers">Mid-Career Researchers</option>
                        <option value="Senior Researchers">Senior Researchers</option>
                        <option value="All Levels">All Levels</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>Stakeholder Engagement</label>
                    <textarea id="impacts-stakeholder" class="large" onchange="markModified('impacts')">{final_data.get('impacts', {}).get('stakeholder_engagement', '')}</textarea>
                </div>

                <div class="form-group">
                    <label>Dissemination Approach</label>
                    <textarea id="impacts-dissemination" class="large" onchange="markModified('impacts')">{final_data.get('impacts', {}).get('dissemination_approach', '')}</textarea>
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

            // Mark sidebar item
            const sidebarItems = document.querySelectorAll('.sidebar-section');
            sidebarItems.forEach(item => {{
                if (item.textContent.toLowerCase().includes(section)) {{
                    item.classList.add('modified');
                }}
            }});

            // Auto-save to localStorage after 2 seconds
            clearTimeout(window.autoSaveTimeout);
            window.autoSaveTimeout = setTimeout(() => {{
                collectAllData();
                localStorage.setItem('cost_report_draft', JSON.stringify(reportData));
            }}, 2000);
        }}

        // Render objectives
        function renderObjectives() {{
            const container = document.getElementById('objectives-container');
            container.innerHTML = '';

            reportData.objectives.forEach((obj, index) => {{
                container.innerHTML += `
                    <div class="objective-editor">
                        <div class="objective-header" onclick="toggleObjective(${{index}})">
                            <span>Objective ${{obj.number}}: ${{obj.title.substring(0, 80)}}...</span>
                            <span>[${{obj.achievement || 'N/A'}}]</span>
                        </div>
                        <div id="obj-body-${{index}}" class="objective-body">
                            <div class="form-group">
                                <label>Title</label>
                                <textarea id="obj-title-${{index}}" onchange="markModified('objectives')">${{obj.title}}</textarea>
                            </div>
                            <div class="stats-grid">
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
                                        <option value="Medium" ${{obj.dependence === 'Medium' ? 'selected' : ''}}>Medium</option>
                                        <option value="Weak" ${{obj.dependence === 'Weak' ? 'selected' : ''}}>Weak</option>
                                    </select>
                                </div>
                            </div>
                            <div class="form-group">
                                <label>Proof Text (Full Achievement Description)</label>
                                <textarea id="obj-proof-${{index}}" class="large" onchange="markModified('objectives')">${{obj.proof_text || ''}}</textarea>
                            </div>
                        </div>
                    </div>
                `;
            }});
        }}

        function toggleObjective(index) {{
            const body = document.getElementById('obj-body-' + index);
            body.classList.toggle('expanded');
        }}

        // Render deliverables
        function renderDeliverables() {{
            const container = document.getElementById('deliverables-container');
            container.innerHTML = '';

            reportData.deliverables.forEach((del, index) => {{
                container.innerHTML += `
                    <div class="deliverable-row">
                        <strong>D${{del.number}}</strong>
                        <input type="text" id="del-title-${{index}}" value="${{del.title}}" onchange="markModified('deliverables')">
                        <select id="del-status-${{index}}" onchange="markModified('deliverables')">
                            <option value="Delivered" ${{del.status === 'Delivered' ? 'selected' : ''}}>Delivered</option>
                            <option value="Not delivered" ${{del.status !== 'Delivered' ? 'selected' : ''}}>Not delivered</option>
                        </select>
                        <select id="del-dependence-${{index}}" onchange="markModified('deliverables')">
                            <option value="Strong" ${{del.dependence === 'Strong' ? 'selected' : ''}}>Strong</option>
                            <option value="Medium" ${{del.dependence === 'Medium' ? 'selected' : ''}}>Medium</option>
                            <option value="Weak" ${{del.dependence === 'Weak' ? 'selected' : ''}}>Weak</option>
                        </select>
                    </div>
                `;
            }});
        }}

        // Render publications
        function renderPublications() {{
            const container = document.getElementById('publications-container');
            container.innerHTML = '';

            reportData.publications.slice(0, 50).forEach((pub, index) => {{
                container.innerHTML += `
                    <div class="publication-item">
                        <div class="pub-num">#${{pub.number || index + 1}}</div>
                        <input type="text" style="width: 100%; margin: 5px 0; padding: 8px;" placeholder="Title" value="${{pub.title || ''}}" id="pub-title-${{index}}" onchange="markModified('publications')">
                        <input type="text" style="width: 100%; margin: 5px 0; padding: 8px;" placeholder="Authors" value="${{pub.authors || ''}}" id="pub-authors-${{index}}" onchange="markModified('publications')">
                        <input type="text" style="width: 60%; margin: 5px 0; padding: 8px;" placeholder="DOI" value="${{pub.doi || ''}}" id="pub-doi-${{index}}" onchange="markModified('publications')">
                    </div>
                `;
            }});

            if (reportData.publications.length > 50) {{
                container.innerHTML += `<p style="padding: 15px; color: var(--cost-gray);">Showing first 50 of ${{reportData.publications.length}} publications. Export JSON to edit all.</p>`;
            }}
        }}

        // Render WG Leaders
        function renderWGLeaders() {{
            const container = document.getElementById('wg-leaders-container');
            container.innerHTML = '';

            const wgLeaders = reportData.leadership?.wg_leaders || [];
            wgLeaders.forEach((wg, index) => {{
                container.innerHTML += `
                    <div style="background: var(--bg-light); padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                        <strong style="color: var(--cost-purple);">WG${{wg.wg_number}}: ${{wg.wg_title?.substring(0, 50)}}...</strong>
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

        // Collect all data from form
        function collectAllData() {{
            // Summary
            reportData.summary.main_objective = document.getElementById('summary-main-objective')?.value || '';
            reportData.summary.description = document.getElementById('summary-description')?.value || '';
            reportData.summary.website = document.getElementById('summary-website')?.value || '';
            reportData.summary.stats = {{
                researchers: parseInt(document.getElementById('stats-researchers')?.value) || 0,
                countries: parseInt(document.getElementById('stats-countries')?.value) || 0,
                cost_countries: parseInt(document.getElementById('stats-cost-countries')?.value) || 0,
                conferences: parseInt(document.getElementById('stats-conferences')?.value) || 0,
                participants: parseInt(document.getElementById('stats-participants')?.value) || 0,
                citations: parseInt(document.getElementById('stats-citations')?.value) || 0
            }};

            // Leadership
            if (reportData.leadership) {{
                reportData.leadership.chair = {{
                    name: document.getElementById('chair-name')?.value || '',
                    email: document.getElementById('chair-email')?.value || '',
                    country: document.getElementById('chair-country')?.value || ''
                }};
                reportData.leadership.vice_chair = {{
                    name: document.getElementById('vicechair-name')?.value || '',
                    email: document.getElementById('vicechair-email')?.value || '',
                    country: document.getElementById('vicechair-country')?.value || ''
                }};
            }}

            // Objectives
            reportData.objectives.forEach((obj, index) => {{
                const titleEl = document.getElementById('obj-title-' + index);
                const achievementEl = document.getElementById('obj-achievement-' + index);
                const dependenceEl = document.getElementById('obj-dependence-' + index);
                const proofEl = document.getElementById('obj-proof-' + index);

                if (titleEl) obj.title = titleEl.value;
                if (achievementEl) obj.achievement = achievementEl.value;
                if (dependenceEl) obj.dependence = dependenceEl.value;
                if (proofEl) obj.proof_text = proofEl.value;
            }});

            // Deliverables
            reportData.deliverables.forEach((del, index) => {{
                const titleEl = document.getElementById('del-title-' + index);
                const statusEl = document.getElementById('del-status-' + index);
                const dependenceEl = document.getElementById('del-dependence-' + index);

                if (titleEl) del.title = titleEl.value;
                if (statusEl) del.status = statusEl.value;
                if (dependenceEl) del.dependence = dependenceEl.value;
            }});

            // Impacts
            if (reportData.impacts) {{
                reportData.impacts.career_benefits = document.getElementById('impacts-career')?.value || '';
                reportData.impacts.experience_level = document.getElementById('impacts-experience')?.value || '';
                reportData.impacts.stakeholder_engagement = document.getElementById('impacts-stakeholder')?.value || '';
                reportData.impacts.dissemination_approach = document.getElementById('impacts-dissemination')?.value || '';
            }}

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
                        types: [{{
                            description: 'JSON files',
                            accept: {{ 'application/json': ['.json'] }}
                        }}]
                    }});
                    const writable = await handle.createWritable();
                    await writable.write(JSON.stringify(reportData, null, 2));
                    await writable.close();
                    updateSaveStatus('saved');
                    showToast('File saved successfully!', 'success');
                    updateLastSaved();
                }} catch (err) {{
                    if (err.name !== 'AbortError') {{
                        showToast('Error saving file: ' + err.message, 'error');
                    }}
                }}
            }} else {{
                // Fallback to download
                exportJSON();
            }}
        }}

        function exportJSON() {{
            collectAllData();
            const dataStr = JSON.stringify(reportData, null, 2);
            const blob = new Blob([dataStr], {{ type: 'application/json' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'final_report_full_' + new Date().toISOString().slice(0,10) + '.json';
            a.click();
            URL.revokeObjectURL(url);
            showToast('JSON exported!', 'success');
        }}

        function exportTXT() {{
            collectAllData();
            let txt = 'COST Action CA19130 - Final Achievement Report\\n';
            txt += '=' .repeat(60) + '\\n\\n';

            txt += 'SUMMARY\\n' + '-'.repeat(40) + '\\n';
            txt += reportData.summary.main_objective + '\\n\\n';
            txt += reportData.summary.description + '\\n\\n';

            txt += 'OBJECTIVES\\n' + '-'.repeat(40) + '\\n';
            reportData.objectives.forEach(obj => {{
                txt += `\\nObjective ${{obj.number}}: ${{obj.title}}\\n`;
                txt += `Achievement: ${{obj.achievement}}\\n`;
                txt += `Proof: ${{obj.proof_text}}\\n`;
            }});

            const blob = new Blob([txt], {{ type: 'text/plain' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'final_report_' + new Date().toISOString().slice(0,10) + '.txt';
            a.click();
            URL.revokeObjectURL(url);
            showToast('TXT exported!', 'success');
        }}

        async function loadFromFile() {{
            if ('showOpenFilePicker' in window) {{
                try {{
                    const [handle] = await window.showOpenFilePicker({{
                        types: [{{
                            description: 'JSON files',
                            accept: {{ 'application/json': ['.json'] }}
                        }}]
                    }});
                    const file = await handle.getFile();
                    const contents = await file.text();
                    reportData = JSON.parse(contents);
                    renderObjectives();
                    renderDeliverables();
                    renderPublications();
                    renderWGLeaders();
                    showToast('File loaded successfully!', 'success');
                }} catch (err) {{
                    if (err.name !== 'AbortError') {{
                        showToast('Error loading file: ' + err.message, 'error');
                    }}
                }}
            }} else {{
                showToast('File System Access API not supported. Use drag and drop or paste JSON.', 'info');
            }}
        }}

        function resetToOriginal() {{
            if (confirm('Reset all changes to original data? This cannot be undone.')) {{
                reportData = JSON.parse(JSON.stringify(originalData));
                localStorage.removeItem('cost_report_draft');
                renderObjectives();
                renderDeliverables();
                renderPublications();
                renderWGLeaders();
                modifiedSections.clear();
                updateSaveStatus('saved');
                showToast('Reset to original data', 'info');
            }}
        }}

        function generatePreview() {{
            collectAllData();
            document.getElementById('json-preview').value = JSON.stringify(reportData, null, 2);
        }}

        // Utility functions
        function updateSaveStatus(status) {{
            const dot = document.getElementById('status-dot');
            const text = document.getElementById('status-text');

            if (status === 'saved') {{
                dot.className = 'status-dot saved';
                text.textContent = 'All changes saved';
                modifiedSections.clear();
                document.querySelectorAll('.sidebar-section.modified').forEach(s => s.classList.remove('modified'));
            }} else if (status === 'modified') {{
                dot.className = 'status-dot modified';
                text.textContent = 'Unsaved changes';
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

        function addPublication() {{
            const newPub = {{
                number: reportData.publications.length + 1,
                title: '',
                authors: '',
                doi: '',
                type: '',
                published_in: '',
                countries: []
            }};
            reportData.publications.push(newPub);
            renderPublications();
            markModified('publications');
        }}

        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {{
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
    print("Generating Report Editor")
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
