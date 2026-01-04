"""
WBP (Work & Budget Plan) Parser for COST Action CA19130.

Parses WBP text files extracted from PDFs to extract:
- Budget summary by category
- Meeting plans
- STSM allocations
- Training school plans

Budget structure in WBP:
A. COST Networking Tools
   (1) Meetings
   (2) Training Schools
   (3) Short Term Scientific Missions (STSM)
   (4) ITC Conference Grant
   (5) COST Action Dissemination
   (6) Other Expenses Related to Scientific Activities (OERSA)
B. Total Science Expenditure (sum of 1-6)
C. FSAC (max 15% of B)
Total Grant (B+C)
"""

import re
from pathlib import Path
from decimal import Decimal
from typing import Dict, List, Optional
from dataclasses import dataclass

from .amount_parser import parse_eur_amount


@dataclass
class WBPCategory:
    """Budget category in Work & Budget Plan."""
    name: str
    budget: Decimal = Decimal("0.00")


@dataclass
class WBPMeeting:
    """Planned meeting in Work & Budget Plan."""
    title: str
    meeting_type: str
    dates: str
    location: str
    itc: bool
    total_cost: Decimal


@dataclass
class WBPData:
    """Complete WBP data structure."""
    grant_period: int
    period_start: str
    period_end: str
    categories: Dict[str, WBPCategory]
    total_science: Decimal  # B. Total Science Expenditure
    fsac: Decimal  # C. FSAC
    total_grant: Decimal  # Total Grant (B+C)
    meetings: List[WBPMeeting]
    raw_text: str = ""


class WBPParser:
    """Parser for WBP (Work & Budget Plan) text files."""

    # WBP files by grant period
    WBP_FILES = {
        1: "WBP-AGA-CA19130-1_13682.txt",
        2: "WBP-AGA-CA19130-2_14713.txt",
        3: "WBP-AGA-CA19130-3_14714.txt",
        4: "WBP-AGA-CA19130-4_15816.txt",
        5: "WBP-AGA-CA19130-5_16959.txt",
    }

    # Category mappings for WBP format
    CATEGORY_MAPPINGS = {
        "(1) meetings": "meetings",
        "(2) training schools": "training_schools",
        "(3) short term scientific missions (stsm)": "stsm",
        "(4) itc conference grant": "itc_conference",
        "(5) cost action dissemination": "dissemination",
        "(6) other expenses related to scientific activities": "oersa",
        "(oersa)": None,  # Skip OERSA label on next line
        "b. total science expenditure (sum of (1) to (6))": "total_science",
        "c. financial and scientific administration and": "fsac",
        "coordination (fsac) (max. of 15% of b)": None,  # Skip continuation
        "total grant (b+c)": "total_grant",
    }

    def __init__(self, source_dir: str):
        """
        Initialize parser with source directory.

        Args:
            source_dir: Directory containing WBP text files
        """
        self.source_dir = Path(source_dir)

    def parse_grant_period(self, gp: int) -> WBPData:
        """
        Parse WBP file for a specific grant period.

        Args:
            gp: Grant period number (1-5)

        Returns:
            WBPData object with all parsed data
        """
        if gp not in self.WBP_FILES:
            raise ValueError(f"Invalid grant period: {gp}. Must be 1-5.")

        filepath = self.source_dir / self.WBP_FILES[gp]
        if not filepath.exists():
            raise FileNotFoundError(f"WBP file not found: {filepath}")

        content = filepath.read_text(encoding='utf-8')

        categories = self._extract_budget_summary(content)

        return WBPData(
            grant_period=gp,
            period_start=self._extract_period_start(content),
            period_end=self._extract_period_end(content),
            categories=categories,
            total_science=categories.get('total_science', WBPCategory('total_science')).budget,
            fsac=categories.get('fsac', WBPCategory('fsac')).budget,
            total_grant=categories.get('total_grant', WBPCategory('total_grant')).budget,
            meetings=self._extract_meetings(content),
            raw_text=content
        )

    def parse_all(self) -> Dict[int, WBPData]:
        """
        Parse all WBP files.

        Returns:
            Dictionary mapping grant period to WBPData
        """
        return {gp: self.parse_grant_period(gp) for gp in self.WBP_FILES.keys()}

    def _extract_period_start(self, content: str) -> str:
        """Extract grant period start date."""
        match = re.search(r'(\d{2}/\d{2}/\d{4})\s+to\s+\d{2}/\d{2}/\d{4}', content)
        return match.group(1) if match else ""

    def _extract_period_end(self, content: str) -> str:
        """Extract grant period end date."""
        match = re.search(r'\d{2}/\d{2}/\d{4}\s+to\s+(\d{2}/\d{2}/\d{4})', content)
        return match.group(1) if match else ""

    def _extract_budget_summary(self, content: str) -> Dict[str, WBPCategory]:
        """Extract budget summary from WBP."""
        categories = {}

        # Find budget summary section
        summary_start = content.find("Work and Budget Plan Summary")
        if summary_start == -1:
            return categories

        # Find end of summary section
        summary_end = content.find("PAGE", summary_start + 50)
        if summary_end == -1:
            summary_end = len(content)

        summary_section = content[summary_start:summary_end]

        # Parse budget lines
        lines = summary_section.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Pattern: Category name followed by amount
            # Example: "(1) Meetings 37,200.00"
            for pattern, normalized in self.CATEGORY_MAPPINGS.items():
                if normalized is None:
                    continue

                if pattern in line.lower():
                    # Try to extract amount from same line
                    amount_match = re.search(r'([\d,\.]+)\s*$', line)
                    if amount_match:
                        amount = parse_eur_amount(amount_match.group(1))
                    else:
                        # Amount might be on next line
                        if i + 1 < len(lines):
                            next_line = lines[i + 1].strip()
                            amount_match = re.search(r'^([\d,\.]+)\s*$', next_line)
                            if amount_match:
                                amount = parse_eur_amount(amount_match.group(1))
                            else:
                                amount = Decimal("0.00")
                        else:
                            amount = Decimal("0.00")

                    categories[normalized] = WBPCategory(
                        name=normalized,
                        budget=amount
                    )
                    break

            i += 1

        # Also try direct pattern matching for standard format
        direct_patterns = [
            (r'\(1\)\s*Meetings\s+([\d,\.]+)', 'meetings'),
            (r'\(2\)\s*Training Schools\s+([\d,\.]+)', 'training_schools'),
            (r'\(3\)\s*Short Term Scientific Missions[^0-9]*([\d,\.]+)', 'stsm'),
            (r'\(4\)\s*ITC Conference Grant\s+([\d,\.]+)', 'itc_conference'),
            (r'\(5\)\s*COST Action Dissemination\s+([\d,\.]+)', 'dissemination'),
            (r'\(6\)\s*Other Expenses[^0-9]*([\d,\.]+)', 'oersa'),
            (r'B\.\s*Total Science Expenditure[^0-9]*([\d,\.]+)', 'total_science'),
            (r'C\.\s*Financial and Scientific Administration[^0-9]*([\d,\.]+)', 'fsac'),
            (r'Total Grant \(B\+C\)\s*([\d,\.]+)', 'total_grant'),
        ]

        for pattern, name in direct_patterns:
            if name not in categories or categories[name].budget == Decimal("0.00"):
                match = re.search(pattern, summary_section, re.IGNORECASE)
                if match:
                    categories[name] = WBPCategory(
                        name=name,
                        budget=parse_eur_amount(match.group(1))
                    )

        return categories

    def _extract_meetings(self, content: str) -> List[WBPMeeting]:
        """Extract planned meetings from WBP."""
        meetings = []

        # Find meetings section
        meetings_start = content.find("Meetings\nOverview")
        if meetings_start == -1:
            meetings_start = content.find("Meetings")
        if meetings_start == -1:
            return meetings

        meetings_end = content.find("Short Term Scientific", meetings_start)
        if meetings_end == -1:
            meetings_end = content.find("Details", meetings_start)
        if meetings_end == -1:
            meetings_end = len(content)

        meetings_section = content[meetings_start:meetings_end]

        # Pattern for meeting entries in overview table
        # Very complex due to PDF extraction artifacts
        # Example: "The darkness of Core Group 18/03/2021 - Bukarest Yes 37,200.00"

        return meetings  # Complex parsing, return empty for now

    def get_category_budget(self, gp: int, category: str) -> Decimal:
        """
        Get budgeted amount for a category in a grant period.

        Args:
            gp: Grant period (1-5)
            category: Category name (normalized)

        Returns:
            Budgeted amount
        """
        data = self.parse_grant_period(gp)
        if category in data.categories:
            return data.categories[category].budget
        return Decimal("0.00")

    def get_total_grant(self, gp: int) -> Decimal:
        """
        Get total grant budget for a grant period.

        Args:
            gp: Grant period (1-5)

        Returns:
            Total grant amount
        """
        data = self.parse_grant_period(gp)
        return data.total_grant
