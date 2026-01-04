"""
Regression tests for space-separated thousands parsing.

CRITICAL BUG IDENTIFIED:
The original data extraction incorrectly parsed EUR amounts with space
as thousands separator:
- "1 011.15" was stored as "11.15" (dropping the thousands)
- "10 300.30" was stored as "300.30"

This affected 175 participant reimbursements across 65 participants.

These regression tests ensure the bug doesn't reoccur.
"""

import pytest
from decimal import Decimal


class TestSpaceSeparatedThousandsParsing:
    """Regression tests for space-separated thousands bug."""

    @pytest.mark.parametrize("raw_text,expected", [
        # Standard cases with space separator
        ("1 011.15", Decimal("1011.15")),
        ("1 000.00", Decimal("1000.00")),
        ("10 300.30", Decimal("10300.30")),
        ("148 194.99", Decimal("148194.99")),

        # Multiple spaces (edge case)
        ("1  011.15", Decimal("1011.15")),

        # Leading/trailing spaces
        (" 1 011.15 ", Decimal("1011.15")),

        # Small amounts (no separator)
        ("600.75", Decimal("600.75")),
        ("99.99", Decimal("99.99")),
        ("0.00", Decimal("0.00")),

        # Negative amounts
        ("-42.50", Decimal("-42.50")),
        ("-1 000.00", Decimal("-1000.00")),

        # With EUR prefix
        ("EUR 1 000.00", Decimal("1000.00")),
        ("EUR 10 300.30", Decimal("10300.30")),

        # With euro symbol
        ("1 000.00", Decimal("1000.00")),

        # Comma as thousands separator (alternative format)
        ("1,011.15", Decimal("1011.15")),
        ("10,300.30", Decimal("10300.30")),
    ])
    def test_parse_eur_amount_space_separated(self, raw_text, expected):
        """parse_eur_amount correctly handles space-separated thousands."""
        from tests.utils import parse_eur_amount

        result = parse_eur_amount(raw_text)
        assert result == expected, \
            f"REGRESSION: '{raw_text}' parsed as {result}, should be {expected}"

    def test_parse_eur_amount_handles_empty(self):
        """parse_eur_amount handles empty/None input gracefully."""
        from tests.utils import parse_eur_amount

        assert parse_eur_amount("") == Decimal("0.00")
        assert parse_eur_amount(None) == Decimal("0.00")
        assert parse_eur_amount("   ") == Decimal("0.00")
        assert parse_eur_amount("-") == Decimal("0.00")


class TestKnownAffectedAmounts:
    """Tests for specific amounts that were known to be affected."""

    # These are real amounts from FFR files that were incorrectly parsed
    KNOWN_AFFECTED_AMOUNTS = [
        # From GP1 Skopje meeting
        ("1 011.15", "Jorg Osterrieder GP1 Skopje"),
        ("1 200.00", "Various GP1-5 participants"),
        ("1 500.00", "Common STSM amount"),
        ("2 030.00", "Galena Pisoni STSM"),
        ("2 450.00", "Apostolos Chalkis STSM"),
        ("2 500.00", "Ioana Coita STSM"),
        ("2 540.00", "Jasone Ramirez-Ayerbe STSM"),
        ("3 500.00", "Common STSM amount"),
        ("20 800.00", "GP1 total STSM"),
        ("10 300.30", "GP1 total meetings"),
    ]

    @pytest.mark.parametrize("amount_text,description", KNOWN_AFFECTED_AMOUNTS)
    def test_known_affected_amounts_parsed_correctly(self, amount_text, description):
        """Known affected amounts are now parsed correctly."""
        from tests.utils import parse_eur_amount

        result = parse_eur_amount(amount_text)
        expected_str = amount_text.replace(" ", "").replace(",", "")
        expected = Decimal(expected_str)

        assert result == expected, \
            f"REGRESSION: {description} - '{amount_text}' parsed as {result}, should be {expected}"


class TestAmountComparisonRobustness:
    """Tests for robust amount comparison."""

    def test_amount_comparison_tolerance(self):
        """Amount comparisons should use appropriate tolerance."""
        from tests.utils import parse_eur_amount

        amount1 = parse_eur_amount("1000.00")
        amount2 = parse_eur_amount("1000.01")

        # Should be within typical EUR tolerance
        diff = abs(amount1 - amount2)
        assert diff <= Decimal("0.05"), "Amount comparison should allow for rounding"

    def test_large_amounts_parsed_correctly(self):
        """Large amounts (100k+) are parsed correctly."""
        from tests.utils import parse_eur_amount

        assert parse_eur_amount("100 000.00") == Decimal("100000.00")
        assert parse_eur_amount("148 194.99") == Decimal("148194.99")
        assert parse_eur_amount("270 315.26") == Decimal("270315.26")


class TestFFRSourceAmounts:
    """Tests that FFR source files can be parsed with correct amounts."""

    @pytest.mark.parametrize("gp", [1, 2, 3, 4, 5])
    def test_ffr_grand_totals_reasonable(self, ffr_parser, gp):
        """FFR grand totals should be reasonable values (not truncated)."""
        data = ffr_parser.parse_grant_period(gp)

        # Minimum expected totals per GP
        min_totals = {
            1: Decimal("40000.00"),
            2: Decimal("30000.00"),
            3: Decimal("160000.00"),
            4: Decimal("250000.00"),
            5: Decimal("260000.00"),
        }

        assert data.total_eligible >= min_totals[gp], \
            f"GP{gp}: Total {data.total_eligible} seems too low (parsing error?)"

    @pytest.mark.parametrize("gp", [1, 5])
    def test_ffr_no_suspiciously_small_totals(self, ffr_parser, gp):
        """No category should have suspiciously small totals."""
        data = ffr_parser.parse_grant_period(gp)

        for cat_name, cat_data in data.categories.items():
            if cat_data.actuals > 0:
                # If a category has activity, it should have reasonable amounts
                # Very small amounts (< 100) for categories like meetings are suspicious
                if cat_name == 'meetings' and cat_data.actuals < Decimal("100.00"):
                    pytest.fail(
                        f"GP{gp}: {cat_name} has suspiciously small amount: {cat_data.actuals}. "
                        "Possible space-separated thousands parsing error."
                    )
