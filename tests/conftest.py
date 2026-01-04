"""
pytest configuration and fixtures for COST Action CA19130 budget verification.

Provides shared fixtures for:
- FFR parsing
- WBP parsing
- HTML parsing
- JSON data loading
"""

import json
import pytest
from pathlib import Path
from decimal import Decimal
from typing import Dict, Any

from tests.utils import FFRParser, WBPParser, HTMLParser, parse_eur_amount


# Paths
PROJECT_ROOT = Path(__file__).parent.parent
FFR_SOURCE_DIR = Path(r"D:\Joerg\Research\slides\COST_Work_and_Budget_Plans\extracted_text")
DATA_DIR = PROJECT_ROOT / "data"
HTML_DIR = PROJECT_ROOT


# Expected totals from FFR exploration (ground truth)
EXPECTED_GP_TOTALS = {
    1: {"budget": Decimal("62985.50"), "actual": Decimal("47459.83")},
    2: {"budget": Decimal("202607.00"), "actual": Decimal("33770.46")},
    3: {"budget": Decimal("169820.50"), "actual": Decimal("166262.38")},
    4: {"budget": Decimal("257925.91"), "actual": Decimal("256854.39")},
    5: {"budget": Decimal("270315.26"), "actual": Decimal("270315.26")},
}

EXPECTED_GRAND_TOTALS = {
    "budget": Decimal("963654.17"),
    "actual": Decimal("774662.32"),
}


# Grant Period list
GRANT_PERIODS = [1, 2, 3, 4, 5]


# Category names
CATEGORIES = [
    'meetings',
    'training_schools',
    'stsm',
    'virtual_mobility',
    'itc_conference',
    'dissemination',
    'oersa',
    'fsac',
]


@pytest.fixture(scope="session")
def ffr_parser() -> FFRParser:
    """Provide FFR parser instance."""
    return FFRParser(str(FFR_SOURCE_DIR))


@pytest.fixture(scope="session")
def wbp_parser() -> WBPParser:
    """Provide WBP parser instance."""
    return WBPParser(str(FFR_SOURCE_DIR))


@pytest.fixture(scope="session")
def html_parser() -> HTMLParser:
    """Provide HTML parser instance."""
    return HTMLParser(str(HTML_DIR))


@pytest.fixture(scope="session")
def all_ffr_data(ffr_parser) -> Dict[int, Any]:
    """Parse all FFR files and return data."""
    return ffr_parser.parse_all()


@pytest.fixture(scope="session")
def all_wbp_data(wbp_parser) -> Dict[int, Any]:
    """Parse all WBP files and return data."""
    return wbp_parser.parse_all()


@pytest.fixture(scope="session")
def budget_data() -> Dict[str, Any]:
    """Load budget_data.json."""
    filepath = DATA_DIR / "budget_data.json"
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


@pytest.fixture(scope="session")
def summary_statistics() -> Dict[str, Any]:
    """Load summary_statistics.json."""
    filepath = DATA_DIR / "summary_statistics.json"
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


@pytest.fixture(scope="session")
def participant_master() -> list:
    """Load participant_master.json."""
    filepath = DATA_DIR / "participant_master.json"
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


@pytest.fixture(scope="session")
def meetings_detailed() -> list:
    """Load meetings_detailed.json."""
    filepath = DATA_DIR / "meetings_detailed.json"
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


@pytest.fixture(scope="session")
def meetings_participants() -> list:
    """Load meetings_participants.json."""
    filepath = DATA_DIR / "meetings_participants.json"
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


@pytest.fixture(scope="session")
def stsm_detailed() -> list:
    """Load stsm_detailed.json."""
    filepath = DATA_DIR / "stsm_detailed.json"
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


@pytest.fixture(scope="session")
def virtual_mobility() -> list:
    """Load virtual_mobility_full.json."""
    filepath = DATA_DIR / "virtual_mobility_full.json"
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


@pytest.fixture(scope="session")
def training_schools() -> list:
    """Load training_school_attendees.json."""
    filepath = DATA_DIR / "training_school_attendees.json"
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


@pytest.fixture
def expected_gp_totals() -> Dict[int, Dict[str, Decimal]]:
    """Expected totals per grant period (ground truth from FFR files)."""
    return EXPECTED_GP_TOTALS


@pytest.fixture
def expected_grand_totals() -> Dict[str, Decimal]:
    """Expected grand totals across all grant periods."""
    return EXPECTED_GRAND_TOTALS


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "gp1: marks tests for Grant Period 1")
    config.addinivalue_line("markers", "gp2: marks tests for Grant Period 2")
    config.addinivalue_line("markers", "gp3: marks tests for Grant Period 3")
    config.addinivalue_line("markers", "gp4: marks tests for Grant Period 4")
    config.addinivalue_line("markers", "gp5: marks tests for Grant Period 5")
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "category: marks tests for a specific budget category")
