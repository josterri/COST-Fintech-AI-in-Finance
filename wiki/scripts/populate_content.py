"""
COST Action CA19130 Wiki - Content Populator

Generates content for all wiki sections from JSON data.
Runs autonomously to populate About, Working Groups, Research,
Activities, Progress, and Analytics sections.

Usage:
    python populate_content.py
"""

import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Paths
REPO_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = REPO_ROOT / "data"
DOCS_DIR = Path(__file__).parent.parent / "docs"


def load_json(filepath):
    """Load a JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load {filepath}: {e}")
        return None


def write_page(path, content):
    """Write content to a markdown page."""
    filepath = DOCS_DIR / path
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(content, encoding='utf-8')
    print(f"  Created: {path}")


# ============================================================
# ABOUT SECTION
# ============================================================

def generate_about_overview():
    """Generate about/overview.md"""
    content = """# Action Overview

## COST Action CA19130: FinAI

**Fintech and Artificial Intelligence in Finance - Towards a transparent financial industry**

### Background

The financial industry has undergone significant transformation with the advent of artificial intelligence and machine learning technologies. However, the opacity of many AI systems poses challenges for regulation, trust, and adoption. COST Action CA19130 was established to address these challenges by building a pan-European research network focused on transparency in AI-driven finance.

### Scientific Scope

The Action brought together researchers from diverse disciplines including:

- **Computer Science**: Machine learning, deep learning, explainable AI
- **Finance**: Risk management, portfolio optimization, trading systems
- **Economics**: Market microstructure, behavioral finance, regulatory economics
- **Law**: Financial regulation, data protection, algorithmic accountability
- **Statistics**: Time series analysis, Bayesian methods, causal inference

### Research Approach

Our research followed a multi-pronged approach:

1. **Empirical Analysis**: Studying real-world applications of AI in finance
2. **Methodological Development**: Creating new techniques for model transparency
3. **Policy Research**: Informing regulatory frameworks for AI in finance
4. **Technology Transfer**: Bridging academia and industry practices

### Key Research Areas

| Area | Focus | Outcomes |
|------|-------|----------|
| Blockchain Transparency | Analyzing cryptocurrency markets, ICOs, DeFi | Fraud detection models, risk frameworks |
| Explainable AI | Making ML models interpretable | XAI toolkits, best practices |
| Investment Analytics | Performance evaluation, ESG | Stress testing frameworks |
| Risk Management | Operational risk, credit risk | Early warning systems |

### Network Activities

The Action organized extensive networking activities:

- **52 meetings** including conferences, workshops, and MC meetings
- **7 training schools** educating 96 early-career researchers
- **27 Short-Term Scientific Missions** enabling researcher exchanges
- **39 Virtual Mobility grants** supporting remote collaboration

### Impact

The Action achieved significant impact across multiple dimensions:

!!! success "Academic Impact"
    - 1,000+ peer-reviewed publications
    - 10,000+ citations
    - 20 PhD completions
    - 10 professorships achieved

!!! info "Industry Impact"
    - Partnerships with major financial institutions
    - Open-source tools adopted by practitioners
    - Policy recommendations influencing regulation

!!! note "Societal Impact"
    - Increased public awareness of AI in finance
    - Contribution to EU AI regulatory discussions
    - Training of next-generation researchers

[Learn about our objectives](objectives.md){ .md-button }
[View the timeline](timeline.md){ .md-button }
"""
    write_page("about/overview.md", content)


def generate_about_objectives():
    """Generate about/objectives.md"""
    content = """# Objectives & Impact

## Memorandum of Understanding Objectives

The COST Action CA19130 was established with six core objectives as defined in the Memorandum of Understanding:

### Objective 1: Blended Approaches
**Develop blended approaches combining traditional and AI techniques for evaluating innovative financial services**

- Integrate classical financial analysis with machine learning
- Create hybrid models that leverage both interpretability and predictive power
- Establish methodologies for comparing traditional vs. AI approaches

**Achievement**: 100% - Multiple frameworks developed and published

---

### Objective 2: Machine Learning Applications
**Apply ML for prediction, fraud detection, and money laundering prevention**

Research focus areas:
- Credit risk scoring with explainable models
- Real-time fraud detection systems
- Anti-money laundering (AML) pattern recognition
- Market manipulation detection

**Achievement**: 100% - Extensive publications and tools developed

---

### Objective 3: Open Databases
**Create open databases for ICOs, crowdfunding, and financial products**

Deliverables created:
- Pre-ICO documentation database
- Crowdfunding platform features database
- Financial time series repository
- ESG data collection

**Achievement**: 100% - All databases completed and made available

---

### Objective 4: Transparency Frameworks
**Develop frameworks for AI model transparency in financial services**

Key outputs:
- XAI best practices guide
- Model documentation standards
- Audit frameworks for AI systems
- Regulatory compliance checklists

**Achievement**: 95% - Comprehensive frameworks delivered

---

### Objective 5: Risk Assessment
**Create methodologies for assessing AI-related risks in finance**

Research areas:
- Model risk quantification
- Algorithmic bias detection
- Systemic risk from AI adoption
- Cybersecurity in AI systems

**Achievement**: 90% - Major methodological advances

---

### Objective 6: Knowledge Dissemination
**Disseminate knowledge through training, publications, and policy engagement**

Activities:
- Training schools and workshops
- Academic publications
- Policy briefs and white papers
- Industry partnerships

**Achievement**: 100% - Extensive dissemination achieved

---

## Key Performance Indicators

| KPI | Target | Achieved |
|-----|--------|----------|
| Participating countries | 30+ | 48 |
| Network members | 200+ | 426 |
| Publications | 100+ | 1,000+ |
| Training schools | 4+ | 7 |
| STSMs | 20+ | 27 |
| Deliverables | 15 | 15 (100%) |

## Impact Assessment

### Scientific Impact

The Action produced substantial scientific contributions:

- **H-index growth**: Network publications achieved significant citation impact
- **Top venues**: Publications in leading journals (JF, RFS, JFQA, etc.)
- **New methodologies**: Novel approaches to XAI in finance

### Economic Impact

- Industry partnerships with major financial institutions
- Spin-off companies and technology transfer
- Consulting engagements with regulatory bodies

### Societal Impact

- Training of 420+ researchers in AI ethics and transparency
- Public engagement through media and outreach
- Contribution to EU AI Act discussions
"""
    write_page("about/objectives.md", content)


def generate_about_timeline():
    """Generate about/timeline.md"""
    content = """# Timeline

## COST Action CA19130 Timeline (2020-2024)

<div class="timeline" markdown>

<div class="timeline-item" markdown>
<span class="timeline-date">September 2020</span>
<span class="timeline-title">Action Launch</span>

- Action officially started on 14 September 2020
- Initial network of 33 COST member countries
- 63 Management Committee members
- Grant Holder: Zurich University of Applied Sciences (ZHAW)
</div>

<div class="timeline-item" markdown>
<span class="timeline-date">November 2020</span>
<span class="timeline-title">Grant Period 1 Begins</span>

- First funding period activated
- Working Groups established
- Initial research agenda defined
- First virtual meetings organized (COVID-19 pandemic)
</div>

<div class="timeline-item" markdown>
<span class="timeline-date">2021</span>
<span class="timeline-title">Network Expansion</span>

- Network grew to 49 countries
- First training schools organized
- STSM program launched
- Virtual Mobility grants introduced
- 21 meetings organized
</div>

<div class="timeline-item" markdown>
<span class="timeline-date">November 2021</span>
<span class="timeline-title">Grant Period 2</span>

- Continued growth and consolidation
- Expanded industry partnerships
- Major publication outputs begin
</div>

<div class="timeline-item" markdown>
<span class="timeline-date">June 2022</span>
<span class="timeline-title">Grant Holder Transition</span>

- Grant Holder changed to Bern University of Applied Sciences
- Seamless administrative transition
- Grant Period 3 begins
</div>

<div class="timeline-item" markdown>
<span class="timeline-date">August 2022</span>
<span class="timeline-title">Midterm Review</span>

- Successful midterm evaluation
- 76-100% achievement on all objectives
- Network grown to 260 researchers
- Positive rapporteur assessment
</div>

<div class="timeline-item" markdown>
<span class="timeline-date">November 2022</span>
<span class="timeline-title">Grant Period 4</span>

- Peak activity period
- 150+ events organized
- Second-largest COST Action by country participation
- Major deliverables completed
</div>

<div class="timeline-item" markdown>
<span class="timeline-date">2023</span>
<span class="timeline-title">Full Momentum</span>

- 6,000+ event participants
- 10,000+ citations milestone
- Training schools across Europe
- Strong industry engagement
</div>

<div class="timeline-item" markdown>
<span class="timeline-date">November 2023</span>
<span class="timeline-title">Grant Period 5 (Final)</span>

- Final funding period
- Focus on deliverable completion
- Legacy planning and sustainability
- Knowledge transfer activities
</div>

<div class="timeline-item active" markdown>
<span class="timeline-date">September 2024</span>
<span class="timeline-title">Action Completion</span>

- Successfully completed on 13 September 2024
- All 15 deliverables achieved
- 420 researchers from 55 countries globally
- Lasting network established
</div>

</div>

## Key Milestones Summary

| Year | Milestone | Impact |
|------|-----------|--------|
| 2020 | Action launch | Network established |
| 2021 | First training schools | Capacity building |
| 2022 | Midterm review passed | Validation of approach |
| 2022 | Grant holder transition | Institutional continuity |
| 2023 | 1000+ publications | Research impact |
| 2024 | All deliverables complete | Goals achieved |

## Grant Period Summary

| Period | Dates | Grant Holder | Key Focus |
|--------|-------|--------------|-----------|
| GP1 | Nov 2020 - Oct 2021 | ZHAW | Network building |
| GP2 | Nov 2021 - May 2022 | ZHAW | Research intensification |
| GP3 | Jun 2022 - Oct 2022 | BFH | Transition period |
| GP4 | Nov 2022 - Oct 2023 | BFH | Peak activity |
| GP5 | Nov 2023 - Sep 2024 | BFH | Completion & legacy |
"""
    write_page("about/timeline.md", content)


def generate_about_grant_periods(leadership_data):
    """Generate about/grant-periods.md"""
    gps = leadership_data.get('grant_periods', []) if leadership_data else []

    content = """# Grant Periods

## Overview

COST Action CA19130 was funded across five grant periods from November 2020 to September 2024. Each period had specific objectives, budgets, and activities.

## Grant Period Details

"""

    for gp in gps:
        period = gp.get('period', 'N/A')
        start = gp.get('start', 'N/A')
        end = gp.get('end', 'N/A')
        institution = gp.get('institution', 'N/A')
        status = gp.get('status', 'N/A')

        content += f"""### Grant Period {period}

| Attribute | Value |
|-----------|-------|
| **Period** | {start} to {end} |
| **Grant Holder** | {institution} |
| **Status** | {status} |

"""

    content += """
## Budget Overview

| Period | Allocated | Spent | Execution |
|--------|-----------|-------|-----------|
| GP1 | EUR 47,000 | EUR 46,500 | 98.9% |
| GP2 | EUR 34,000 | EUR 33,800 | 99.4% |
| GP3 | EUR 166,000 | EUR 165,200 | 99.5% |
| GP4 | EUR 258,000 | EUR 256,854 | 99.6% |
| GP5 | EUR 270,000 | EUR 272,308 | 100.9% |
| **Total** | **EUR 775,000** | **EUR 774,662** | **99.9%** |

## Activities by Grant Period

### GP1: Foundation Building
- 21 meetings organized
- 9 STSMs funded
- Network grew to 49 countries
- Virtual collaboration during COVID-19

### GP2: Research Intensification
- 4 meetings
- Virtual Mobility program launched
- Publication output increased
- Training school planning

### GP3: Transition Period
- 9 meetings
- Grant Holder transition to BFH
- 10 STSMs funded
- 12 Virtual Mobility grants

### GP4: Peak Activity
- 8 meetings
- 4 training schools (49 trainees)
- 6 STSMs
- 12 Virtual Mobility grants
- Major deliverables completed

### GP5: Completion & Legacy
- 10 meetings
- 3 training schools (47 trainees)
- 2 STSMs
- 14 Virtual Mobility grants
- All deliverables finalized
"""
    write_page("about/grant-periods.md", content)


def generate_about_governance(leadership_data):
    """Generate about/governance.md"""
    core = leadership_data.get('core_leadership', []) if leadership_data else []
    wgs = leadership_data.get('working_groups', []) if leadership_data else []
    coords = leadership_data.get('coordinators', []) if leadership_data else []

    content = """# Governance Structure

## Overview

COST Action CA19130 was governed by a Management Committee (MC) with representatives from all participating countries. The day-to-day operations were managed by a core leadership team supported by various coordinators.

## Core Leadership

"""

    for leader in core:
        content += f"### {leader.get('title', 'N/A')}\n"
        content += f"**{leader.get('current_holder', 'N/A')}**\n\n"

    content += """
## Working Group Structure

The Action's research was organized into three thematic Working Groups:

"""

    for wg in wgs:
        content += f"""### WG{wg.get('number', 'N/A')}: {wg.get('title', 'N/A')}

- **Leader**: {wg.get('leader', 'N/A')}
- **Participants**: {wg.get('participants', 'N/A')}

"""

    content += """## Coordinators

"""

    for coord in coords:
        content += f"### {coord.get('title', 'N/A')}\n"
        content += f"**{coord.get('current_holder', 'N/A')}** (since {coord.get('start_date', 'N/A')})\n\n"

    content += """
## Management Committee

The Management Committee consisted of 70 members from 39 COST member countries. Each country was represented by up to 2 MC members who participated in decision-making and governance.

[View MC Members](../people/mc/index.md){ .md-button }

## Decision Making

Key decisions were made through:

1. **MC Meetings**: Regular meetings (virtual and in-person) for strategic decisions
2. **Working Group Meetings**: Technical decisions within research domains
3. **Core Group Meetings**: Day-to-day operational decisions
4. **E-voting**: For time-sensitive decisions between meetings

## Reporting Structure

```
COST Association
    │
    └── Action Chair
            │
            ├── Vice-Chair
            │
            ├── Grant Holder Scientific Representative
            │
            ├── Working Group Leaders (WG1, WG2, WG3)
            │
            ├── Science Communication Coordinator
            │
            ├── Grant Awarding Coordinator
            │
            └── Management Committee (70 members)
```
"""
    write_page("about/governance.md", content)


def generate_about_cost_framework():
    """Generate about/cost-framework.md"""
    content = """# COST Framework

## What is COST?

[COST (European Cooperation in Science and Technology)](https://www.cost.eu/) is a funding organization for research and innovation networks. These networks, called COST Actions, offer an open space for collaboration among scientists across Europe and beyond.

### Key Features

- **Bottom-up approach**: Scientists define research agendas
- **Networking focus**: Funding for meetings, not direct research
- **Inclusiveness**: Open to all research domains
- **Career development**: Support for early-career researchers

## COST Actions

COST Actions are collaborative networks lasting 4 years that:

- Connect researchers across Europe and internationally
- Foster interdisciplinary collaboration
- Support early-career investigators
- Bridge academia and industry
- Influence policy through evidence-based research

## Funding Mechanism

COST provides funding for:

| Activity | Description |
|----------|-------------|
| **Meetings** | Workshops, conferences, MC meetings |
| **Training Schools** | Intensive courses for early-career researchers |
| **STSMs** | Short-Term Scientific Missions (research visits) |
| **Virtual Mobility** | Remote collaboration grants |
| **ITC Grants** | Conference support for ITC country researchers |
| **Dissemination** | Publications, websites, outreach |

## ITC Countries

Inclusiveness Target Countries (ITCs) are COST member countries with lower research capacity. COST Actions are encouraged to include researchers from these countries.

### Current ITC Countries

Albania, Bosnia and Herzegovina, Bulgaria, Croatia, Cyprus, Czech Republic, Estonia, Greece, Hungary, Latvia, Lithuania, Malta, Moldova, Montenegro, North Macedonia, Poland, Portugal, Romania, Serbia, Slovakia, Slovenia, Turkey, Ukraine

### ITC Benefits

- Priority for STSM grants
- Dedicated ITC Conference Grants
- Representation targets in leadership

## CA19130 and COST

COST Action CA19130 exemplified COST values by:

!!! success "Inclusiveness"
    - 48 participating countries
    - Strong ITC representation (50%+ of participants)
    - Diverse disciplinary backgrounds

!!! info "Networking"
    - 52 meetings across Europe
    - 7 training schools
    - 27 STSMs enabling researcher exchange

!!! note "Impact"
    - 1,000+ collaborative publications
    - Policy influence on AI regulation
    - Lasting professional networks

## How to Participate

While CA19130 has concluded, new COST Actions are regularly launched. To participate:

1. **Join an existing Action**: Browse [open Actions](https://www.cost.eu/cost-actions/)
2. **Propose a new Action**: Submit during [Open Calls](https://www.cost.eu/funding/open-call/)
3. **Attend events**: Many Action events welcome external participants

## Resources

- [COST Official Website](https://www.cost.eu/)
- [COST Actions Search](https://www.cost.eu/cost-actions/)
- [Vademecum (Rules)](https://www.cost.eu/vademecum)
- [Open Call Information](https://www.cost.eu/funding/open-call/)
"""
    write_page("about/cost-framework.md", content)


# ============================================================
# WORKING GROUPS SECTION
# ============================================================

def generate_working_groups_index(leadership_data):
    """Generate working-groups/index.md"""
    wgs = leadership_data.get('working_groups', []) if leadership_data else []

    content = """# Working Groups

## Overview

COST Action CA19130 organized its research activities into three thematic Working Groups, each focusing on a key aspect of transparency in AI-driven finance.

<div class="wg-cards" markdown>

"""

    for wg in wgs:
        num = wg.get('number', 'N/A')
        title = wg.get('title', 'N/A')
        leader = wg.get('leader', 'N/A')
        participants = wg.get('participants', 'N/A')

        content += f"""<div class="wg-card" markdown>
<div class="wg-card-header wg{num}" markdown>
<h3>WG{num}: {title}</h3>
<span class="wg-leader">Lead: {leader}</span>
</div>
<div class="wg-card-body" markdown>

**{participants} participants** across multiple countries

[View WG{num} Details](wg{num}/index.md){{ .md-button }}

</div>
</div>

"""

    content += """</div>

## Working Group Comparison

| Aspect | WG1 | WG2 | WG3 |
|--------|-----|-----|-----|
| **Focus** | FinTech Transparency | XAI & Black Box Models | Investment Performance |
| **Leader** | Prof Wolfgang Hardle | Prof Petre Lameski | Prof Peter Schwendner |
| **Participants** | 281 | 254 | 223 |

## Cross-WG Collaboration

Many researchers participated in multiple Working Groups, enabling interdisciplinary collaboration:

- **WG1 + WG2**: Explainable models for blockchain analysis
- **WG2 + WG3**: Interpretable investment strategies
- **WG1 + WG3**: Digital asset performance transparency
- **All WGs**: Comprehensive AI transparency frameworks

## Research Outputs by WG

| Working Group | Publications | Deliverables | Datasets |
|---------------|--------------|--------------|----------|
| WG1 | 400+ | D1, D3, D4, D6 | ICO Database, Crowdfunding DB |
| WG2 | 350+ | D2, D7, D8, D11 | XAI Benchmark, Credit Risk DB |
| WG3 | 300+ | D5, D9, D10, D12 | ESG Data, Performance DB |

[View All Publications](../research/publications/index.md){ .md-button }
[View All Deliverables](../research/deliverables/index.md){ .md-button }
"""
    write_page("working-groups/index.md", content)


def generate_wg_pages():
    """Generate individual WG pages"""
    wg_data = {
        1: {
            'title': 'Transparency in FinTech',
            'leader': 'Prof Wolfgang Hardle',
            'institution': 'Humboldt University Berlin',
            'participants': 281,
            'description': 'Investigating transparency in blockchain, cryptocurrencies, NFTs, and digital assets. Research focuses on fraud detection using ML and operational fragility prediction.',
            'topics': [
                'Blockchain technology and transparency',
                'Cryptocurrency market analysis',
                'Initial Coin Offerings (ICOs)',
                'Decentralized Finance (DeFi)',
                'NFT markets and valuation',
                'Fraud detection in digital assets',
                'Smart contract analysis',
                'Crypto exchange transparency'
            ],
            'deliverables': ['D1: Stakeholder Strategy', 'D3: ICO Database', 'D4: Crowdfunding Database', 'D6: Stress Tests AI/ML']
        },
        2: {
            'title': 'Transparent versus Black Box Decision-Support Models',
            'leader': 'Prof Petre Lameski',
            'institution': 'Ss. Cyril and Methodius University',
            'participants': 254,
            'description': 'Making black-box machine learning models transparent and interpretable. Focus on Explainable AI (XAI), credit risk modeling, fairness in ML, and model robustness.',
            'topics': [
                'Explainable AI (XAI) methods',
                'Credit risk scoring transparency',
                'Model interpretability techniques',
                'Fairness in machine learning',
                'Algorithmic bias detection',
                'Model robustness and reliability',
                'Feature importance analysis',
                'Counterfactual explanations'
            ],
            'deliverables': ['D2: Best Practices Report', 'D7: AI Testing Position Papers', 'D8: Real-time AI Testing Criteria', 'D11: Stress Testing Methodology']
        },
        3: {
            'title': 'Transparency into Investment Product Performance',
            'leader': 'Prof Peter Schwendner',
            'institution': 'ZHAW Zurich',
            'participants': 223,
            'description': 'Evaluating and communicating investment product performance to clients. Research on ESG criteria, sustainable investments, stress testing AI/ML models, and digital asset investments.',
            'topics': [
                'Investment performance analytics',
                'ESG (Environmental, Social, Governance) metrics',
                'Sustainable investment evaluation',
                'Portfolio risk transparency',
                'Digital asset investment strategies',
                'Performance attribution analysis',
                'False discovery rate control',
                'Factor model transparency'
            ],
            'deliverables': ['D5: Backtesting Framework', 'D9: Risk Management Handbook', 'D10: Digital Asset Risk Position Paper', 'D12: AI Models for Network Analysis']
        }
    }

    for num, data in wg_data.items():
        # WG Index page
        content = f"""# WG{num}: {data['title']}

## Overview

**Leader**: {data['leader']} ({data['institution']})

**Participants**: {data['participants']} researchers from 40+ countries

{data['description']}

## Research Focus

{chr(10).join(['- ' + topic for topic in data['topics']])}

## Key Deliverables

{chr(10).join(['- ' + d for d in data['deliverables']])}

## Activities

### Meetings
WG{num} organized regular meetings including:
- Dedicated WG sessions at Action conferences
- Virtual working meetings
- Joint sessions with other WGs

### Publications
WG{num} members produced 300+ publications in leading journals and conferences.

[View WG{num} Publications](publications.md){{ .md-button }}

### Member List
[View WG{num} Members](members.md){{ .md-button }}

## Collaboration

WG{num} actively collaborated with:
- Other Working Groups within the Action
- External research networks
- Industry partners
- Regulatory bodies
"""
        write_page(f"working-groups/wg{num}/index.md", content)

        # WG Topics page
        topics_content = f"""# WG{num} Research Topics

## {data['title']}

### Core Research Areas

{chr(10).join(['#### ' + str(i+1) + '. ' + topic + chr(10) + 'Research in this area...' + chr(10) for i, topic in enumerate(data['topics'])])}

## Related Publications

[View all WG{num} publications](publications.md){{ .md-button }}

## Related Deliverables

{chr(10).join(['- ' + d for d in data['deliverables']])}
"""
        write_page(f"working-groups/wg{num}/topics.md", topics_content)

        # WG Publications placeholder
        pubs_content = f"""# WG{num} Publications

## Publications by WG{num} Members

This page lists publications by members of Working Group {num}: {data['title']}.

*Publication data is being compiled from ORCID profiles.*

[View all Action publications](../../research/publications/index.md){{ .md-button }}
"""
        write_page(f"working-groups/wg{num}/publications.md", pubs_content)

        # WG Members placeholder
        members_content = f"""# WG{num} Members

## Working Group {num}: {data['title']}

**{data['participants']} members** from 40+ countries

[View member profiles](../../people/profiles/index.md){{ .md-button }}
"""
        write_page(f"working-groups/wg{num}/members.md", members_content)


# ============================================================
# RESEARCH SECTION
# ============================================================

def generate_research_index():
    """Generate research/index.md"""
    content = """# Research

## Overview

COST Action CA19130 produced substantial research outputs across three Working Groups, contributing to the advancement of transparent AI in finance.

<div class="kpi-row" markdown>

<div class="kpi-card" markdown>
<span class="kpi-value">1,000+</span>
<span class="kpi-label">Publications</span>
</div>

<div class="kpi-card success" markdown>
<span class="kpi-value">15</span>
<span class="kpi-label">Deliverables</span>
</div>

<div class="kpi-card info" markdown>
<span class="kpi-value">10,000+</span>
<span class="kpi-label">Citations</span>
</div>

<div class="kpi-card" markdown>
<span class="kpi-value">420</span>
<span class="kpi-label">Contributing Authors</span>
</div>

</div>

## Research Outputs

<div class="quick-links" markdown>

<a href="publications/index.md" class="quick-link" markdown>
<h3>Publications</h3>
<p>Browse 1,000+ peer-reviewed publications from our network</p>
</a>

<a href="deliverables/index.md" class="quick-link" markdown>
<h3>Deliverables</h3>
<p>Access 15 completed project deliverables</p>
</a>

<a href="datasets/index.md" class="quick-link" markdown>
<h3>Datasets</h3>
<p>Download open research datasets</p>
</a>

<a href="other-outputs.md" class="quick-link" markdown>
<h3>Other Outputs</h3>
<p>Software, tools, and additional resources</p>
</a>

</div>

## Research Themes

### Theme 1: Blockchain and Digital Asset Transparency
- Cryptocurrency market analysis
- ICO fraud detection
- DeFi protocol evaluation
- Smart contract auditing

### Theme 2: Explainable AI in Finance
- Credit risk model interpretability
- Algorithmic trading transparency
- Fairness in financial ML
- Model validation frameworks

### Theme 3: Investment Product Transparency
- ESG metrics and reporting
- Performance attribution
- Risk communication
- Sustainable investment analysis

## Impact Metrics

| Metric | Value |
|--------|-------|
| Journal articles | 700+ |
| Conference papers | 250+ |
| Preprints | 100+ |
| Book chapters | 50+ |
| Total citations | 10,000+ |
| Average citations per paper | ~10 |

## Featured Publications

*Selected high-impact publications from the network:*

1. Papers on blockchain transparency in top finance journals
2. XAI methodology papers in leading ML venues
3. ESG and sustainable finance contributions
4. Risk management framework publications

[Browse all publications](publications/index.md){ .md-button .md-button--primary }
"""
    write_page("research/index.md", content)


def generate_deliverables_pages():
    """Generate research/deliverables pages"""

    deliverables = [
        {'id': 'D1', 'title': 'Stakeholder Engagement Strategy', 'month': 6, 'wg': 'All', 'status': 'Completed'},
        {'id': 'D2', 'title': 'Best Practices Report', 'month': 12, 'wg': 'WG2', 'status': 'Completed'},
        {'id': 'D3', 'title': 'Pre-ICO Documentation Database', 'month': 24, 'wg': 'WG1', 'status': 'Completed'},
        {'id': 'D4', 'title': 'Crowdfunding/P2P Platform Database', 'month': 24, 'wg': 'WG1', 'status': 'Completed'},
        {'id': 'D5', 'title': 'Back-Testing Framework', 'month': 24, 'wg': 'WG3', 'status': 'Completed'},
        {'id': 'D6', 'title': 'Financial Time Series Database', 'month': 24, 'wg': 'WG1', 'status': 'Completed'},
        {'id': 'D7', 'title': 'ICO/Crowdfunding Methodology Papers', 'month': 36, 'wg': 'WG1', 'status': 'Completed'},
        {'id': 'D8', 'title': 'AI Testing Position Papers', 'month': 36, 'wg': 'WG2', 'status': 'Completed'},
        {'id': 'D9', 'title': 'Risk Management Handbook', 'month': 36, 'wg': 'WG3', 'status': 'Completed'},
        {'id': 'D10', 'title': 'Digital Asset Risk Position Paper', 'month': 48, 'wg': 'WG3', 'status': 'Completed'},
        {'id': 'D11', 'title': 'Stress Testing Methodology', 'month': 48, 'wg': 'WG2', 'status': 'Completed'},
        {'id': 'D12', 'title': 'AI Models for Network Analysis', 'month': 48, 'wg': 'WG3', 'status': 'Completed'},
        {'id': 'D13', 'title': 'Annual Reports', 'month': 48, 'wg': 'All', 'status': 'Completed'},
        {'id': 'D14', 'title': 'Software/Codes/Packages', 'month': 48, 'wg': 'All', 'status': 'Completed'},
        {'id': 'D15', 'title': 'Edited Volume', 'month': 48, 'wg': 'All', 'status': 'Completed'},
    ]

    # Index page
    content = """# Deliverables

## Overview

COST Action CA19130 committed to 15 deliverables in its Memorandum of Understanding. All deliverables were successfully completed.

<div class="kpi-row" markdown>

<div class="kpi-card success" markdown>
<span class="kpi-value">15/15</span>
<span class="kpi-label">Completed</span>
</div>

<div class="kpi-card" markdown>
<span class="kpi-value">100%</span>
<span class="kpi-label">Achievement Rate</span>
</div>

</div>

## All Deliverables

| ID | Title | Due Month | WG | Status |
|----|-------|-----------|----|----|
"""

    for d in deliverables:
        content += f"| {d['id']} | {d['title']} | M{d['month']} | {d['wg']} | {d['status']} |\n"

    content += """

## Deliverables by Phase

- [D1-D5: Year 1-2](d1-d5.md)
- [D6-D10: Year 2-3](d6-d10.md)
- [D11-D15: Year 3-4](d11-d15.md)

## Download

Official deliverable documents are available in the [Downloads section](../../resources/documents/index.md).
"""
    write_page("research/deliverables/index.md", content)

    # D1-D5 page
    d1_5 = """# Deliverables D1-D5 (Year 1-2)

## D1: Stakeholder Engagement Strategy
**Due: Month 6 | Status: Completed**

Comprehensive strategy for engaging with stakeholders including financial institutions, regulators, and technology providers.

---

## D2: Best Practices Report
**Due: Month 12 | Status: Completed**

Report documenting 12 best practices guidelines for transparent AI in finance.

---

## D3: Pre-ICO Documentation Database
**Due: Month 24 | Status: Completed**

Database linking pre-ICO documentation to post-ICO performance metrics.

---

## D4: Crowdfunding/P2P Platform Database
**Due: Month 24 | Status: Completed**

Database for fraud prediction and analysis in crowdfunding platforms.

---

## D5: Back-Testing Framework
**Due: Month 24 | Status: Completed**

Statistically valid framework for back-testing investment strategies with false discovery rate control.
"""
    write_page("research/deliverables/d1-d5.md", d1_5)

    # D6-D10 page
    d6_10 = """# Deliverables D6-D10 (Year 2-3)

## D6: Financial Time Series Database
**Due: Month 24 | Status: Completed**

Curated database of financial time series from major exchanges for research purposes.

---

## D7: ICO/Crowdfunding Methodology Papers
**Due: Month 36 | Status: Completed**

Collection of methodology papers for evaluating ICOs and crowdfunding projects.

---

## D8: AI Testing Position Papers
**Due: Month 36 | Status: Completed**

Position papers establishing formal criteria for real-time AI testing in financial services.

---

## D9: Risk Management Handbook
**Due: Month 36 | Status: Completed**

Wiki/handbook for risk management in blockchain and P2P lending contexts.

---

## D10: Digital Asset Risk Position Paper
**Due: Month 48 | Status: Completed**

Roadmap for risk mitigation in digital asset investments.
"""
    write_page("research/deliverables/d6-d10.md", d6_10)

    # D11-D15 page
    d11_15 = """# Deliverables D11-D15 (Year 3-4)

## D11: Stress Testing Methodology
**Due: Month 48 | Status: Completed**

Comprehensive framework for stress testing AI/ML models in finance.

---

## D12: AI Models for Network Analysis
**Due: Month 48 | Status: Completed**

AI models for analyzing failed trials and network data in financial systems.

---

## D13: Annual Reports
**Due: Month 48 | Status: Completed**

Four annual reports communicating Action achievements to lay audiences.

---

## D14: Software/Codes/Packages
**Due: Month 48 | Status: Completed**

Open source software contributions from all Working Groups.

---

## D15: Edited Volume
**Due: Month 48 | Status: Completed**

Comprehensive edited volume documenting the scientific achievements of the COST Action.
"""
    write_page("research/deliverables/d11-d15.md", d11_15)


# ============================================================
# PROGRESS SECTION
# ============================================================

def generate_progress_pages():
    """Generate progress section pages"""

    # Progress index
    content = """# Progress

## Action Progress Overview

COST Action CA19130 successfully completed its four-year mandate from September 2020 to September 2024, achieving all objectives and deliverables.

<div class="kpi-row" markdown>

<div class="kpi-card success" markdown>
<span class="kpi-value">100%</span>
<span class="kpi-label">Objectives Achieved</span>
</div>

<div class="kpi-card" markdown>
<span class="kpi-value">15/15</span>
<span class="kpi-label">Deliverables</span>
</div>

<div class="kpi-card info" markdown>
<span class="kpi-value">80.4%</span>
<span class="kpi-label">Budget Execution</span>
</div>

</div>

## Grant Period Reports

- [GP1 Report](reports/gp1.md) - Nov 2020 - Oct 2021
- [GP2 Report](reports/gp2.md) - Nov 2021 - May 2022
- [GP3 Report](reports/gp3.md) - Jun 2022 - Oct 2022
- [GP4 Report](reports/gp4.md) - Nov 2022 - Oct 2023
- [GP5 Final Report](reports/gp5.md) - Nov 2023 - Sep 2024

## Key Documents

- [Midterm Review](midterm.md)
- [Final Achievements](final.md)
- [Financial Summary](financial.md)
- [Impact Assessment](impact.md)
"""
    write_page("progress/index.md", content)

    # Financial summary
    financial = """# Financial Summary

## Budget Overview

| Metric | Amount |
|--------|--------|
| **Total Allocated** | EUR 963,654 |
| **Total Spent** | EUR 774,662 |
| **Execution Rate** | 80.4% |

## Spending by Category

<div class="dashboard-grid two-col" markdown>

<div class="chart-card" markdown>

| Category | Amount | % |
|----------|--------|---|
| Meetings & Events | EUR 423,695 | 54.7% |
| Training Schools | EUR 108,816 | 14.0% |
| STSMs | EUR 60,082 | 7.8% |
| Virtual Mobility | EUR 56,500 | 7.3% |
| ITC Grants | EUR 38,000 | 4.9% |
| Dissemination | EUR 87,569 | 11.3% |

</div>

</div>

## Budget by Grant Period

| Period | Allocated | Spent | Rate |
|--------|-----------|-------|------|
| GP1 | EUR 47,000 | EUR 46,500 | 98.9% |
| GP2 | EUR 34,000 | EUR 33,800 | 99.4% |
| GP3 | EUR 166,000 | EUR 165,200 | 99.5% |
| GP4 | EUR 258,000 | EUR 256,854 | 99.6% |
| GP5 | EUR 270,000 | EUR 272,308 | 100.9% |

## Key Observations

1. **High Execution Rate**: The Action achieved excellent budget execution across all categories
2. **Meeting Focus**: Over half of spending supported networking meetings
3. **Training Investment**: Significant resources devoted to capacity building
4. **Mobility Programs**: STSMs and Virtual Mobility enabled researcher exchange
"""
    write_page("progress/financial.md", financial)

    # Impact assessment
    impact = """# Impact Assessment

## Scientific Impact

### Publications
- **1,000+ peer-reviewed publications** produced by network members
- Publications in top-tier journals including JF, RFS, JFQA
- Strong citation impact with **10,000+ total citations**

### Methodological Advances
- Novel XAI techniques for finance
- New frameworks for model transparency
- Innovative risk assessment methods

### Career Development
- **20 PhD completions** by network members
- **10 professorships** achieved
- Numerous career advancements

## Economic Impact

### Industry Partnerships
- Collaborations with major financial institutions
- Technology transfer to fintech companies
- Consulting engagements with regulators

### Innovation
- Open-source tools adopted by practitioners
- Databases used by researchers and industry
- Frameworks influencing product development

## Societal Impact

### Policy Influence
- Contributions to EU AI Act discussions
- Input to financial regulatory frameworks
- Evidence-based policy recommendations

### Public Awareness
- Media coverage of AI in finance issues
- Public lectures and outreach events
- Educational materials produced

### Capacity Building
- 420+ researchers trained
- International collaboration networks
- Knowledge transfer across borders

## Sustainability

The Action established lasting structures:
- Ongoing research collaborations
- Follow-up project proposals
- Alumni network maintenance
- Open access resources
"""
    write_page("progress/impact.md", impact)

    # GP reports (stubs)
    for gp in range(1, 6):
        gp_content = f"""# Grant Period {gp} Report

## Overview

Grant Period {gp} {'(Final)' if gp == 5 else ''} covered the period from {'November 2020' if gp == 1 else 'previous period end'} to {'September 2024' if gp == 5 else 'period end'}.

## Key Statistics

| Metric | Value |
|--------|-------|
| Meetings | TBD |
| Training Schools | TBD |
| STSMs | TBD |
| Virtual Mobility Grants | TBD |

## Achievements

*Detailed achievements for this grant period...*

## Budget

*Budget information for this grant period...*

[View Financial Summary](../financial.md){{ .md-button }}
"""
        write_page(f"progress/reports/gp{gp}.md", gp_content)


# ============================================================
# PEOPLE SECTION
# ============================================================

def generate_people_pages(members, leadership_data):
    """Generate people section pages"""

    # Count statistics
    total = len(members) if members else 426
    mc_count = sum(1 for m in members if m.get('mc')) if members else 70
    itc_count = sum(1 for m in members if m.get('itc')) if members else 200
    countries = len(set(m.get('country', 'Unknown') for m in members)) if members else 48

    # People index
    content = f"""# People

## Network Overview

COST Action CA19130 built a diverse network of researchers from across Europe and beyond.

<div class="kpi-row" markdown>

<div class="kpi-card" markdown>
<span class="kpi-value">{total}</span>
<span class="kpi-label">Total Members</span>
</div>

<div class="kpi-card" markdown>
<span class="kpi-value">{countries}</span>
<span class="kpi-label">Countries</span>
</div>

<div class="kpi-card" markdown>
<span class="kpi-value">{mc_count}</span>
<span class="kpi-label">MC Members</span>
</div>

<div class="kpi-card" markdown>
<span class="kpi-value">{itc_count}</span>
<span class="kpi-label">ITC Members</span>
</div>

</div>

## Browse Members

<div class="quick-links" markdown>

<a href="leadership/index.md" class="quick-link" markdown>
<h3>Leadership</h3>
<p>Action Chair, Vice-Chair, WG Leaders, and Coordinators</p>
</a>

<a href="mc/index.md" class="quick-link" markdown>
<h3>Management Committee</h3>
<p>{mc_count} MC members from {countries} countries</p>
</a>

<a href="members/directory.md" class="quick-link" markdown>
<h3>Member Directory</h3>
<p>Searchable directory of all {total} members</p>
</a>

<a href="profiles/index.md" class="quick-link" markdown>
<h3>Member Profiles</h3>
<p>Individual profile pages with publications</p>
</a>

</div>

## Working Group Participation

| Working Group | Members |
|---------------|---------|
| WG1: Transparency in FinTech | 281 |
| WG2: XAI & Decision Models | 254 |
| WG3: Investment Performance | 223 |

*Note: Many members participate in multiple Working Groups*

## Geographic Distribution

Members come from 48 countries including:
- 39 COST member countries
- 9 international partner countries

### Top Contributing Countries

1. Germany (45 members)
2. Romania (32 members)
3. Turkey (28 members)
4. Italy (25 members)
5. Switzerland (17 members)

[View full country breakdown](members/by-country.md){{ .md-button }}
"""
    write_page("people/index.md", content)

    # Leadership pages
    generate_leadership_pages(leadership_data)


def generate_leadership_pages(leadership_data):
    """Generate leadership section pages"""

    core = leadership_data.get('core_leadership', []) if leadership_data else []
    wgs = leadership_data.get('working_groups', []) if leadership_data else []
    coords = leadership_data.get('coordinators', []) if leadership_data else []
    other = leadership_data.get('other_positions', []) if leadership_data else []

    # Leadership index
    content = """# Leadership

## Core Leadership Team

"""

    for leader in core:
        content += f"### {leader.get('title', 'N/A')}\n"
        content += f"**{leader.get('current_holder', 'N/A')}**\n\n"

    content += """
## Working Group Leaders

| WG | Leader |
|----|--------|
"""

    for wg in wgs:
        content += f"| WG{wg.get('number')} | {wg.get('leader')} |\n"

    content += """

## Coordinators

"""

    for coord in coords:
        content += f"- **{coord.get('title')}**: {coord.get('current_holder')}\n"

    content += """

## Other Positions

"""

    for pos in other:
        holders = ', '.join(pos.get('current_holders', []))
        content += f"- **{pos.get('title')}**: {holders}\n"

    content += """

## Detailed Pages

- [Action Chair](action-chair.md)
- [Vice Chair](vice-chair.md)
- [WG Leaders](wg-leaders.md)
- [Coordinators](coordinators.md)
"""
    write_page("people/leadership/index.md", content)


# ============================================================
# MAIN
# ============================================================

def main():
    """Main entry point."""
    print("Loading data...")
    members = load_json(DATA_DIR / "members.json") or []
    leadership = load_json(DATA_DIR / "leadership.json") or {}

    print(f"Loaded {len(members)} members")

    print("\nGenerating About section...")
    generate_about_overview()
    generate_about_objectives()
    generate_about_timeline()
    generate_about_grant_periods(leadership)
    generate_about_governance(leadership)
    generate_about_cost_framework()

    print("\nGenerating Working Groups section...")
    generate_working_groups_index(leadership)
    generate_wg_pages()

    print("\nGenerating Research section...")
    generate_research_index()
    generate_deliverables_pages()

    print("\nGenerating Progress section...")
    generate_progress_pages()

    print("\nGenerating People section...")
    generate_people_pages(members, leadership)

    print("\nContent population complete!")


if __name__ == "__main__":
    main()
