"""
HTML Parser for COST Action CA19130 website pages.

Extracts displayed budget/expenditure values from HTML pages for verification:
- ffr1-5.html: FFR summary pages
- gp1-5.html: Grant period pages
- overview.html: Summary overview page
"""

import re
from pathlib import Path
from decimal import Decimal
from typing import Dict, Optional, List
from dataclasses import dataclass

from .amount_parser import parse_eur_amount


@dataclass
class HTMLPageData:
    """Data extracted from an HTML page."""
    page_name: str
    title: str
    budget_amounts: Dict[str, Decimal]
    actual_amounts: Dict[str, Decimal]
    totals: Dict[str, Decimal]
    raw_html: str = ""


class HTMLParser:
    """Parser for COST Action HTML pages."""

    def __init__(self, html_dir: str):
        """
        Initialize parser with HTML directory.

        Args:
            html_dir: Directory containing HTML files (COST-Fintech-AI-in-Finance)
        """
        self.html_dir = Path(html_dir)

    def parse_ffr_page(self, gp: int) -> HTMLPageData:
        """
        Parse FFR HTML page for a grant period.

        Args:
            gp: Grant period (1-5)

        Returns:
            HTMLPageData with extracted values
        """
        filepath = self.html_dir / "financial-reports" / f"ffr{gp}.html"
        if not filepath.exists():
            raise FileNotFoundError(f"FFR page not found: {filepath}")

        content = filepath.read_text(encoding='utf-8')

        return HTMLPageData(
            page_name=f"ffr{gp}.html",
            title=self._extract_title(content),
            budget_amounts=self._extract_amounts_from_table(content, 1),  # Budget column
            actual_amounts=self._extract_amounts_from_table(content, 2),  # Actual column
            totals=self._extract_stat_boxes(content),
            raw_html=content
        )

    def parse_gp_page(self, gp: int) -> HTMLPageData:
        """
        Parse Grant Period HTML page.

        Args:
            gp: Grant period (1-5)

        Returns:
            HTMLPageData with extracted values
        """
        filepath = self.html_dir / "work-budget-plans" / f"gp{gp}.html"
        if not filepath.exists():
            raise FileNotFoundError(f"GP page not found: {filepath}")

        content = filepath.read_text(encoding='utf-8')

        return HTMLPageData(
            page_name=f"gp{gp}.html",
            title=self._extract_title(content),
            budget_amounts=self._extract_amounts_from_table(content, 1),
            actual_amounts={},
            totals=self._extract_stat_boxes(content),
            raw_html=content
        )

    def parse_overview_page(self) -> HTMLPageData:
        """
        Parse overview HTML page.

        Returns:
            HTMLPageData with extracted values
        """
        filepath = self.html_dir / "financial-reports" / "overview.html"
        if not filepath.exists():
            raise FileNotFoundError(f"Overview page not found: {filepath}")

        content = filepath.read_text(encoding='utf-8')

        return HTMLPageData(
            page_name="overview.html",
            title=self._extract_title(content),
            budget_amounts=self._extract_all_amounts(content),
            actual_amounts={},
            totals=self._extract_stat_boxes(content),
            raw_html=content
        )

    def _extract_title(self, content: str) -> str:
        """Extract page title."""
        match = re.search(r'<title>([^<]+)</title>', content)
        return match.group(1) if match else ""

    def _extract_stat_boxes(self, content: str) -> Dict[str, Decimal]:
        """Extract values from stat boxes (Budget EUR, Actual EUR, etc.)."""
        amounts = {}

        # Pattern for stat boxes: <div class="num">270,315</div><div class="label">Budget EUR</div>
        stat_pattern = r'<div class="num">([\d,\.]+)</div>\s*<div class="label">([^<]+)</div>'

        for match in re.finditer(stat_pattern, content):
            value = match.group(1)
            label = match.group(2).strip().lower()

            # Normalize label
            if 'budget' in label:
                key = 'budget_total'
            elif 'actual' in label:
                key = 'actual_total'
            elif 'utilization' in label:
                key = 'utilization'
            else:
                key = label.replace(' ', '_')

            amounts[key] = parse_eur_amount(value)

        return amounts

    def _extract_amounts_from_table(self, content: str, column: int) -> Dict[str, Decimal]:
        """
        Extract amounts from HTML table.

        Args:
            content: HTML content
            column: Column index (1=Budget, 2=Actual, etc.)

        Returns:
            Dictionary of category -> amount
        """
        amounts = {}

        # Find table rows with amounts
        # Pattern: <tr><td>Category</td><td class="amount">X</td><td class="amount">Y</td>...</tr>
        row_pattern = r'<tr[^>]*>\s*<td>([^<]+)</td>\s*(?:<td[^>]*>[\d,\.\s]+</td>\s*){' + str(column - 1) + r'}<td[^>]*class="amount"[^>]*>([\d,\.]+)</td>'

        for match in re.finditer(row_pattern, content):
            category = match.group(1).strip().lower()
            value = match.group(2)

            # Normalize category name
            normalized = self._normalize_category(category)
            if normalized:
                amounts[normalized] = parse_eur_amount(value)

        # Also try simpler pattern
        simple_pattern = r'<td>([^<]+)</td>\s*<td class="amount">([\d,\.]+)</td>'
        for match in re.finditer(simple_pattern, content):
            category = match.group(1).strip().lower()
            value = match.group(2)

            normalized = self._normalize_category(category)
            if normalized and normalized not in amounts:
                amounts[normalized] = parse_eur_amount(value)

        return amounts

    def _extract_all_amounts(self, content: str) -> Dict[str, Decimal]:
        """Extract all amounts with class="amount" from content."""
        amounts = {}

        # Pattern for amounts with preceding category text
        pattern = r'<td>([^<]+)</td>\s*<td class="amount">([\d,\.]+)</td>'

        for match in re.finditer(pattern, content):
            category = match.group(1).strip().lower()
            value = match.group(2)

            normalized = self._normalize_category(category)
            if normalized:
                amounts[normalized] = parse_eur_amount(value)

        return amounts

    def _normalize_category(self, category: str) -> Optional[str]:
        """Normalize category name for consistent lookup."""
        category = category.lower().strip()

        mappings = {
            'meetings': 'meetings',
            'training schools': 'training_schools',
            'stsms': 'stsm',
            'stms': 'stsm',
            'short-term scientific mission': 'stsm',
            'virtual mobility': 'virtual_mobility',
            'itc conference grants': 'itc_conference',
            'dissemination': 'dissemination',
            'oersa': 'oersa',
            'fsac': 'fsac',
            'total': 'total',
        }

        for pattern, normalized in mappings.items():
            if pattern in category:
                return normalized

        return None

    def get_displayed_amount(self, page: str, category: str, amount_type: str = 'actual') -> Decimal:
        """
        Get a displayed amount from an HTML page.

        Args:
            page: Page name (e.g., 'ffr5', 'gp1', 'overview')
            category: Category name
            amount_type: 'budget' or 'actual'

        Returns:
            Displayed amount
        """
        if page.startswith('ffr'):
            gp = int(page[3])
            data = self.parse_ffr_page(gp)
        elif page.startswith('gp'):
            gp = int(page[2])
            data = self.parse_gp_page(gp)
        elif page == 'overview':
            data = self.parse_overview_page()
        else:
            raise ValueError(f"Unknown page: {page}")

        if amount_type == 'budget':
            return data.budget_amounts.get(category, Decimal("0.00"))
        else:
            return data.actual_amounts.get(category, Decimal("0.00"))
