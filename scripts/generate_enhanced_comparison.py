"""
Generate an enhanced comparison HTML page with interactive visualizations.
Uses Chart.js for charts and adds comprehensive metrics.
"""

import json
from pathlib import Path
from datetime import datetime


def generate_enhanced_comparison_html(comparison_data, final_data, midterm_data):
    """Generate an enhanced comparison HTML page with visualizations."""

    # Calculate additional metrics
    objectives_comp = comparison_data.get("objectives_comparison", [])
    deliverables_comp = comparison_data.get("deliverables_comparison", [])

    # Count achievement levels
    midterm_achievements = {"76-100%": 0, "51-75%": 0, "26-50%": 0, "0-25%": 0}
    final_achievements = {"76-100%": 0, "51-75%": 0, "26-50%": 0, "0-25%": 0}

    for obj in objectives_comp:
        m_ach = obj.get("midterm_achievement", "")
        f_ach = obj.get("final_achievement", "")
        if m_ach in midterm_achievements:
            midterm_achievements[m_ach] += 1
        if f_ach in final_achievements:
            final_achievements[f_ach] += 1

    # Deliverable status counts
    midterm_delivered = sum(1 for d in deliverables_comp if d.get("midterm_status") == "Delivered")
    final_delivered = sum(1 for d in deliverables_comp if d.get("final_status") == "Delivered")
    total_deliverables = len(deliverables_comp)

    # Objectives that improved
    improved_objectives = sum(1 for obj in objectives_comp if obj.get("achievement_changed", False))

    summary_comp = comparison_data.get("summary_comparison", {})
    pub_comp = comparison_data.get("publications_comparison", {})

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>COST CA19130 - Enhanced Comparison Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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
            background: linear-gradient(135deg, var(--cost-purple), var(--cost-blue));
            color: white;
            padding: 25px 40px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}

        .header h1 {{ font-size: 2em; margin-bottom: 5px; }}
        .header .subtitle {{ opacity: 0.9; font-size: 1.1em; }}

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
            font-weight: 500;
        }}

        .nav-bar a:hover, .nav-bar a.active {{
            background: var(--cost-purple);
            color: white;
        }}

        .container {{
            max-width: 1800px;
            margin: 0 auto;
            padding: 30px 40px;
        }}

        /* Dashboard Grid */
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }}

        .metric-card {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            text-align: center;
            position: relative;
            overflow: hidden;
        }}

        .metric-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--cost-purple), var(--cost-blue));
        }}

        .metric-card .label {{
            color: var(--cost-gray);
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}

        .metric-card .values {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
            margin-bottom: 10px;
        }}

        .metric-card .midterm {{ color: var(--cost-blue); font-size: 2em; font-weight: bold; }}
        .metric-card .arrow {{ color: var(--cost-green); font-size: 1.5em; }}
        .metric-card .final {{ color: var(--cost-purple); font-size: 2em; font-weight: bold; }}
        .metric-card .change {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }}
        .metric-card .change.positive {{ background: #d4edda; color: #155724; }}
        .metric-card .change.neutral {{ background: #e2e3e5; color: #383d41; }}

        /* Chart Section */
        .chart-section {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 25px;
            margin-bottom: 30px;
        }}

        .chart-card {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}

        .chart-card h3 {{
            color: var(--cost-purple);
            margin-bottom: 20px;
            font-size: 1.2em;
            border-bottom: 2px solid var(--bg-light);
            padding-bottom: 10px;
        }}

        .chart-container {{
            position: relative;
            height: 300px;
        }}

        /* Progress Section */
        .progress-section {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            margin-bottom: 30px;
        }}

        .progress-section h2 {{
            color: var(--cost-purple);
            margin-bottom: 20px;
        }}

        .progress-item {{
            margin-bottom: 20px;
        }}

        .progress-label {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-weight: 500;
        }}

        .progress-bar-container {{
            background: #e9ecef;
            border-radius: 10px;
            height: 12px;
            overflow: hidden;
            position: relative;
        }}

        .progress-bar {{
            height: 100%;
            border-radius: 10px;
            transition: width 0.5s ease;
        }}

        .progress-bar.midterm {{
            background: var(--cost-blue);
            position: absolute;
            opacity: 0.5;
        }}

        .progress-bar.final {{
            background: var(--cost-purple);
            position: relative;
            z-index: 1;
        }}

        /* Objectives Grid */
        .objectives-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 30px;
        }}

        .obj-mini-card {{
            background: white;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            cursor: pointer;
            transition: all 0.2s;
            border-left: 4px solid var(--cost-purple);
        }}

        .obj-mini-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}

        .obj-mini-card.improved {{
            border-left-color: var(--cost-green);
        }}

        .obj-mini-card .obj-num {{
            font-weight: bold;
            color: var(--cost-purple);
            font-size: 1.1em;
        }}

        .obj-mini-card .obj-achievement {{
            display: flex;
            gap: 10px;
            margin-top: 8px;
            font-size: 0.85em;
        }}

        .obj-mini-card .badge {{
            padding: 3px 8px;
            border-radius: 4px;
            font-weight: 500;
        }}

        .badge-blue {{ background: #cce5ff; color: #004085; }}
        .badge-purple {{ background: #e2d5f0; color: #5B2D8A; }}
        .badge-green {{ background: #d4edda; color: #155724; }}

        /* Deliverables Table */
        .deliverables-section {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            margin-bottom: 30px;
        }}

        .deliverables-table {{
            width: 100%;
            border-collapse: collapse;
        }}

        .deliverables-table th {{
            background: var(--cost-purple);
            color: white;
            padding: 15px;
            text-align: left;
        }}

        .deliverables-table td {{
            padding: 12px 15px;
            border-bottom: 1px solid var(--border-color);
        }}

        .deliverables-table tr:hover {{
            background: var(--bg-light);
        }}

        .status-badge {{
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 500;
        }}

        .status-delivered {{ background: #d4edda; color: #155724; }}
        .status-not-delivered {{ background: #f8d7da; color: #721c24; }}

        /* Modal */
        .modal {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }}

        .modal.active {{ display: flex; }}

        .modal-content {{
            background: white;
            border-radius: 12px;
            max-width: 900px;
            max-height: 80vh;
            overflow-y: auto;
            padding: 30px;
            position: relative;
        }}

        .modal-close {{
            position: absolute;
            top: 15px;
            right: 20px;
            font-size: 1.5em;
            cursor: pointer;
            color: var(--cost-gray);
        }}

        .modal-close:hover {{ color: var(--cost-purple); }}

        .comparison-columns {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 20px;
        }}

        .comparison-col {{
            border: 1px solid var(--border-color);
            border-radius: 8px;
            overflow: hidden;
        }}

        .comparison-col .col-header {{
            padding: 12px 15px;
            font-weight: bold;
            color: white;
        }}

        .comparison-col .col-header.midterm {{ background: var(--cost-blue); }}
        .comparison-col .col-header.final {{ background: var(--cost-purple); }}

        .comparison-col .col-content {{
            padding: 15px;
            font-size: 0.95em;
            max-height: 300px;
            overflow-y: auto;
            line-height: 1.7;
        }}

        /* Footer */
        .footer {{
            background: var(--cost-purple);
            color: white;
            text-align: center;
            padding: 25px;
            margin-top: 40px;
        }}

        .footer a {{ color: white; }}

        /* Tabs */
        .tabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 25px;
            flex-wrap: wrap;
        }}

        .tab-btn {{
            padding: 12px 24px;
            border: none;
            background: white;
            cursor: pointer;
            border-radius: 8px;
            font-size: 0.95em;
            transition: all 0.2s;
            color: #333;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }}

        .tab-btn:hover {{ background: var(--cost-purple-light); color: white; }}
        .tab-btn.active {{ background: var(--cost-purple); color: white; }}

        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}

        /* Highlight Changes */
        .highlight-change {{
            background: linear-gradient(90deg, #fff3cd 0%, transparent 100%);
            padding: 2px 5px;
            border-radius: 3px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>COST Action CA19130: Enhanced Comparison Dashboard</h1>
        <div class="subtitle">Mid-Term (24 months) vs Final Report (48 months) | Interactive Analytics</div>
    </div>

    <div class="nav-bar">
        <a href="index.html">Home</a>
        <a href="final-action-chair-report-full.html">Final Report</a>
        <a href="midterm-action-chair-report-full.html">Mid-Term Report</a>
        <a href="comparison-action-chair-full.html">Basic Comparison</a>
        <a href="comparison-enhanced.html" class="active">Enhanced Comparison</a>
        <a href="report-editor.html">Report Editor</a>
    </div>

    <div class="container">
        <!-- Key Metrics Dashboard -->
        <div class="dashboard-grid">
            <div class="metric-card">
                <div class="label">Researchers</div>
                <div class="values">
                    <span class="midterm">{summary_comp.get('researchers', {}).get('midterm', 'N/A')}</span>
                    <span class="arrow">-></span>
                    <span class="final">{summary_comp.get('researchers', {}).get('final', 'N/A')}</span>
                </div>
                <span class="change positive">+{summary_comp.get('researchers', {}).get('change', 0)} (+{round(summary_comp.get('researchers', {}).get('change', 0) / max(summary_comp.get('researchers', {}).get('midterm', 1), 1) * 100)}%)</span>
            </div>
            <div class="metric-card">
                <div class="label">Countries</div>
                <div class="values">
                    <span class="midterm">{summary_comp.get('countries', {}).get('midterm', 'N/A')}</span>
                    <span class="arrow">-></span>
                    <span class="final">{summary_comp.get('countries', {}).get('final', 'N/A')}</span>
                </div>
                <span class="change positive">+{summary_comp.get('countries', {}).get('change', 0)} countries</span>
            </div>
            <div class="metric-card">
                <div class="label">Publications</div>
                <div class="values">
                    <span class="midterm">{pub_comp.get('midterm_count', 'N/A')}</span>
                    <span class="arrow">-></span>
                    <span class="final">{pub_comp.get('final_count', 'N/A')}</span>
                </div>
                <span class="change positive">+{pub_comp.get('new_publications', 0)} new</span>
            </div>
            <div class="metric-card">
                <div class="label">Deliverables Completed</div>
                <div class="values">
                    <span class="midterm">{midterm_delivered}/{total_deliverables}</span>
                    <span class="arrow">-></span>
                    <span class="final">{final_delivered}/{total_deliverables}</span>
                </div>
                <span class="change positive">+{final_delivered - midterm_delivered} delivered</span>
            </div>
        </div>

        <!-- Tabs -->
        <div class="tabs">
            <button class="tab-btn active" onclick="showTab('overview')">Overview Charts</button>
            <button class="tab-btn" onclick="showTab('objectives')">Objectives Analysis</button>
            <button class="tab-btn" onclick="showTab('deliverables')">Deliverables Status</button>
            <button class="tab-btn" onclick="showTab('timeline')">Progress Timeline</button>
        </div>

        <!-- Overview Tab -->
        <div id="overview" class="tab-content active">
            <div class="chart-section">
                <div class="chart-card">
                    <h3>Achievement Level Distribution</h3>
                    <div class="chart-container">
                        <canvas id="achievementChart"></canvas>
                    </div>
                </div>
                <div class="chart-card">
                    <h3>Deliverables Progress</h3>
                    <div class="chart-container">
                        <canvas id="deliverablesChart"></canvas>
                    </div>
                </div>
                <div class="chart-card">
                    <h3>Network Growth</h3>
                    <div class="chart-container">
                        <canvas id="growthChart"></canvas>
                    </div>
                </div>
                <div class="chart-card">
                    <h3>Objectives Improvement</h3>
                    <div class="chart-container">
                        <canvas id="improvementChart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- Objectives Tab -->
        <div id="objectives" class="tab-content">
            <div class="progress-section">
                <h2>All 16 Objectives - Achievement Comparison</h2>
                <p style="margin-bottom: 20px; color: var(--cost-gray);">Click any objective card for detailed comparison. Blue = Mid-Term, Purple = Final.</p>

                <div class="objectives-grid">
"""

    # Generate objective mini cards
    for obj in objectives_comp:
        improved_class = "improved" if obj.get("achievement_changed", False) else ""
        html += f"""
                    <div class="obj-mini-card {improved_class}" onclick="showObjectiveModal({obj['number']})">
                        <div class="obj-num">Objective {obj['number']}</div>
                        <div class="obj-achievement">
                            <span class="badge badge-blue">{obj.get('midterm_achievement', 'N/A')}</span>
                            <span>-></span>
                            <span class="badge badge-purple">{obj.get('final_achievement', 'N/A')}</span>
                            {'<span class="badge badge-green">Improved</span>' if obj.get('achievement_changed', False) else ''}
                        </div>
                    </div>
"""

    html += """
                </div>
            </div>

            <div class="progress-section">
                <h2>Achievement Progress Bars</h2>
"""

    # Progress bars for each objective
    for obj in objectives_comp:
        midterm_pct = {"76-100%": 88, "51-75%": 63, "26-50%": 38, "0-25%": 12}.get(obj.get("midterm_achievement", ""), 0)
        final_pct = {"76-100%": 88, "51-75%": 63, "26-50%": 38, "0-25%": 12}.get(obj.get("final_achievement", ""), 0)

        html += f"""
                <div class="progress-item">
                    <div class="progress-label">
                        <span>Obj {obj['number']}: {obj.get('title', '')[:60]}...</span>
                        <span>{obj.get('midterm_achievement', 'N/A')} -> {obj.get('final_achievement', 'N/A')}</span>
                    </div>
                    <div class="progress-bar-container">
                        <div class="progress-bar midterm" style="width: {midterm_pct}%"></div>
                        <div class="progress-bar final" style="width: {final_pct}%"></div>
                    </div>
                </div>
"""

    html += """
            </div>
        </div>

        <!-- Deliverables Tab -->
        <div id="deliverables" class="tab-content">
            <div class="deliverables-section">
                <h2>Deliverables Status Comparison</h2>
                <table class="deliverables-table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Deliverable</th>
                            <th>Mid-Term</th>
                            <th>Final</th>
                            <th>Status Change</th>
                        </tr>
                    </thead>
                    <tbody>
"""

    for d in deliverables_comp:
        midterm_class = "status-delivered" if d.get("midterm_status") == "Delivered" else "status-not-delivered"
        final_class = "status-delivered" if d.get("final_status") == "Delivered" else "status-not-delivered"
        changed = d.get("status_changed", False)

        html += f"""
                        <tr>
                            <td><strong>D{d.get('number', '')}</strong></td>
                            <td>{d.get('title', '')[:80]}...</td>
                            <td><span class="status-badge {midterm_class}">{d.get('midterm_status', 'N/A')}</span></td>
                            <td><span class="status-badge {final_class}">{d.get('final_status', 'N/A')}</span></td>
                            <td>{'<span class="status-badge status-delivered">Newly Delivered</span>' if changed else '<span class="status-badge" style="background: #e2e3e5;">No Change</span>'}</td>
                        </tr>
"""

    html += """
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Timeline Tab -->
        <div id="timeline" class="tab-content">
            <div class="chart-card" style="margin-bottom: 30px;">
                <h3>Action Timeline & Milestones</h3>
                <div class="chart-container" style="height: 400px;">
                    <canvas id="timelineChart"></canvas>
                </div>
            </div>

            <div class="progress-section">
                <h2>Key Milestones</h2>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px;">
                    <div style="padding: 20px; background: var(--bg-light); border-radius: 8px; border-left: 4px solid var(--cost-blue);">
                        <h4 style="color: var(--cost-blue);">Mid-Term (Month 24)</h4>
                        <p>Period: 14/09/2020 - 14/09/2022</p>
                        <ul style="margin-top: 10px;">
                            <li>260 researchers across 49 countries</li>
                            <li>1/15 deliverables completed</li>
                            <li>99 co-authored publications</li>
                            <li>150+ research events organized</li>
                        </ul>
                    </div>
                    <div style="padding: 20px; background: var(--bg-light); border-radius: 8px; border-left: 4px solid var(--cost-purple);">
                        <h4 style="color: var(--cost-purple);">Final Report (Month 48)</h4>
                        <p>Period: 14/09/2020 - 13/09/2024</p>
                        <ul style="margin-top: 10px;">
                            <li>420 researchers across 55 countries</li>
                            <li>15/15 deliverables completed</li>
                            <li>99 co-authored publications (in report)</li>
                            <li>7000+ event participants</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Objective Modal -->
    <div id="objectiveModal" class="modal">
        <div class="modal-content">
            <span class="modal-close" onclick="closeModal()">&times;</span>
            <h2 id="modalTitle">Objective Details</h2>
            <div id="modalContent"></div>
        </div>
    </div>

    <div class="footer">
        <p>COST Action CA19130: Fintech and Artificial Intelligence in Finance</p>
        <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")} |
           <a href="https://www.fintech-ai-finance.com/" target="_blank">Action Website</a> |
           <a href="https://github.com/Digital-AI-Finance/COST-Fintech-AI-in-Finance" target="_blank">GitHub</a>
        </p>
    </div>

    <script>
        // Store objectives data for modal
        const objectivesData = {json.dumps(objectives_comp, indent=2)};

        // Tab switching
        function showTab(tabId) {{
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            event.target.classList.add('active');
        }}

        // Modal functions
        function showObjectiveModal(num) {{
            const obj = objectivesData.find(o => o.number === num);
            if (!obj) return;

            document.getElementById('modalTitle').textContent = 'Objective ' + num + ' Comparison';
            document.getElementById('modalContent').innerHTML = `
                <p style="margin-bottom: 15px; color: var(--cost-gray);">${{escapeHtml(obj.title)}}</p>
                <div style="margin-bottom: 15px;">
                    <span class="badge badge-blue" style="padding: 5px 15px;">Mid-Term: ${{obj.midterm_achievement}}</span>
                    <span style="margin: 0 10px;">-></span>
                    <span class="badge badge-purple" style="padding: 5px 15px;">Final: ${{obj.final_achievement}}</span>
                    ${{obj.achievement_changed ? '<span class="badge badge-green" style="padding: 5px 15px; margin-left: 10px;">Improved!</span>' : ''}}
                </div>
                <div class="comparison-columns">
                    <div class="comparison-col">
                        <div class="col-header midterm">Mid-Term Proof</div>
                        <div class="col-content">${{escapeHtml(obj.midterm_proof || 'No proof text available')}}</div>
                    </div>
                    <div class="comparison-col">
                        <div class="col-header final">Final Proof</div>
                        <div class="col-content">${{escapeHtml(obj.final_proof || 'No proof text available')}}</div>
                    </div>
                </div>
            `;
            document.getElementById('objectiveModal').classList.add('active');
        }}

        function closeModal() {{
            document.getElementById('objectiveModal').classList.remove('active');
        }}

        function escapeHtml(text) {{
            if (!text) return '';
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML.replace(/\\n/g, '<br>');
        }}

        // Close modal on outside click
        document.getElementById('objectiveModal').addEventListener('click', function(e) {{
            if (e.target === this) closeModal();
        }});

        // Charts
        document.addEventListener('DOMContentLoaded', function() {{
            // Achievement Distribution Chart
            new Chart(document.getElementById('achievementChart'), {{
                type: 'bar',
                data: {{
                    labels: ['76-100%', '51-75%', '26-50%', '0-25%'],
                    datasets: [
                        {{
                            label: 'Mid-Term',
                            data: [{midterm_achievements['76-100%']}, {midterm_achievements['51-75%']}, {midterm_achievements['26-50%']}, {midterm_achievements['0-25%']}],
                            backgroundColor: 'rgba(43, 95, 158, 0.7)',
                            borderColor: 'rgba(43, 95, 158, 1)',
                            borderWidth: 1
                        }},
                        {{
                            label: 'Final',
                            data: [{final_achievements['76-100%']}, {final_achievements['51-75%']}, {final_achievements['26-50%']}, {final_achievements['0-25%']}],
                            backgroundColor: 'rgba(91, 45, 138, 0.7)',
                            borderColor: 'rgba(91, 45, 138, 1)',
                            borderWidth: 1
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ position: 'top' }},
                        title: {{ display: false }}
                    }},
                    scales: {{
                        y: {{ beginAtZero: true, ticks: {{ stepSize: 2 }} }}
                    }}
                }}
            }});

            // Deliverables Progress Chart
            new Chart(document.getElementById('deliverablesChart'), {{
                type: 'doughnut',
                data: {{
                    labels: ['Mid-Term Delivered', 'Final New Deliveries', 'Not Delivered'],
                    datasets: [{{
                        data: [{midterm_delivered}, {final_delivered - midterm_delivered}, {total_deliverables - final_delivered}],
                        backgroundColor: [
                            'rgba(43, 95, 158, 0.8)',
                            'rgba(91, 45, 138, 0.8)',
                            'rgba(220, 53, 69, 0.3)'
                        ],
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ position: 'bottom' }}
                    }}
                }}
            }});

            // Network Growth Chart
            new Chart(document.getElementById('growthChart'), {{
                type: 'bar',
                data: {{
                    labels: ['Researchers', 'Countries', 'Publications'],
                    datasets: [
                        {{
                            label: 'Mid-Term',
                            data: [{summary_comp.get('researchers', {}).get('midterm', 0)}, {summary_comp.get('countries', {}).get('midterm', 0)}, {pub_comp.get('midterm_count', 0)}],
                            backgroundColor: 'rgba(43, 95, 158, 0.7)'
                        }},
                        {{
                            label: 'Final',
                            data: [{summary_comp.get('researchers', {}).get('final', 0)}, {summary_comp.get('countries', {}).get('final', 0)}, {pub_comp.get('final_count', 0)}],
                            backgroundColor: 'rgba(91, 45, 138, 0.7)'
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ position: 'top' }}
                    }},
                    scales: {{
                        y: {{ beginAtZero: true }}
                    }}
                }}
            }});

            // Objectives Improvement Chart
            new Chart(document.getElementById('improvementChart'), {{
                type: 'pie',
                data: {{
                    labels: ['Improved', 'Maintained'],
                    datasets: [{{
                        data: [{improved_objectives}, {16 - improved_objectives}],
                        backgroundColor: [
                            'rgba(40, 167, 69, 0.8)',
                            'rgba(108, 117, 125, 0.5)'
                        ],
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ position: 'bottom' }},
                        title: {{
                            display: true,
                            text: '{improved_objectives} of 16 objectives improved'
                        }}
                    }}
                }}
            }});

            // Timeline Chart
            new Chart(document.getElementById('timelineChart'), {{
                type: 'line',
                data: {{
                    labels: ['Start (M0)', 'Year 1 (M12)', 'Mid-Term (M24)', 'Year 3 (M36)', 'Final (M48)'],
                    datasets: [
                        {{
                            label: 'Researchers',
                            data: [50, 150, 260, 340, 420],
                            borderColor: 'rgba(91, 45, 138, 1)',
                            backgroundColor: 'rgba(91, 45, 138, 0.1)',
                            fill: true,
                            tension: 0.3
                        }},
                        {{
                            label: 'Countries',
                            data: [20, 35, 49, 52, 55],
                            borderColor: 'rgba(43, 95, 158, 1)',
                            backgroundColor: 'rgba(43, 95, 158, 0.1)',
                            fill: true,
                            tension: 0.3,
                            yAxisID: 'y1'
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {{
                        mode: 'index',
                        intersect: false
                    }},
                    plugins: {{
                        legend: {{ position: 'top' }}
                    }},
                    scales: {{
                        y: {{
                            type: 'linear',
                            display: true,
                            position: 'left',
                            title: {{ display: true, text: 'Researchers' }}
                        }},
                        y1: {{
                            type: 'linear',
                            display: true,
                            position: 'right',
                            title: {{ display: true, text: 'Countries' }},
                            grid: {{ drawOnChartArea: false }}
                        }}
                    }}
                }}
            }});
        }});
    </script>
</body>
</html>
"""

    return html


def main():
    """Main function to generate enhanced comparison HTML."""
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / "data"

    print("=" * 60)
    print("Generating Enhanced Comparison Dashboard")
    print("=" * 60)

    # Load data
    print("\nLoading JSON data...")
    with open(data_dir / "final_report_full.json", 'r', encoding='utf-8') as f:
        final_data = json.load(f)
    with open(data_dir / "midterm_report_full.json", 'r', encoding='utf-8') as f:
        midterm_data = json.load(f)
    with open(data_dir / "report_comparison.json", 'r', encoding='utf-8') as f:
        comparison_data = json.load(f)

    # Generate HTML
    print("Generating enhanced comparison HTML...")
    html = generate_enhanced_comparison_html(comparison_data, final_data, midterm_data)

    output_path = base_dir / "comparison-enhanced.html"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"\nSaved: {output_path}")
    print(f"Size: {len(html):,} characters")
    print("\n" + "=" * 60)
    print("Done!")


if __name__ == "__main__":
    main()
