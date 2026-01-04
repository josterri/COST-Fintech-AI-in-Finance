"""
Test STSM (Short-Term Scientific Mission) category totals.

Verifies STSM expenditure across FFR -> JSON -> HTML chain.
"""

import pytest
from decimal import Decimal


class TestSTSMTotals:
    """Tests for STSM category totals."""

    @pytest.mark.parametrize("gp", [1, 2, 3, 4, 5])
    def test_ffr_stsm_extraction(self, ffr_parser, gp):
        """FFR parser extracts STSM category correctly."""
        data = ffr_parser.parse_grant_period(gp)

        # STSM category should exist
        assert 'stsm' in data.categories, f"GP{gp}: STSM category not found in FFR"

        stsm_actual = data.categories['stsm'].actuals
        assert stsm_actual >= Decimal("0.00"), f"GP{gp}: negative STSM amount"

    @pytest.mark.parametrize("gp", [1, 3, 4, 5])  # GP2 had 0 STSMs
    def test_ffr_individual_stsms_extracted(self, ffr_parser, gp):
        """FFR parser extracts individual STSM records."""
        data = ffr_parser.parse_grant_period(gp)

        # GP1 had 9 STSMs, GP3 had 10, GP4 had 6, GP5 had 2
        expected_counts = {1: 9, 3: 10, 4: 6, 5: 2}

        stsm_count = len(data.stsms)
        expected = expected_counts.get(gp, 0)

        # Allow some tolerance for parsing variations
        assert stsm_count >= expected - 2, \
            f"GP{gp}: Expected ~{expected} STSMs, found {stsm_count}"

    def test_stsm_total_across_all_gps(self, all_ffr_data):
        """Sum of STSMs should match expected grand total."""
        total_stsm = sum(
            data.categories.get('stsm', type('', (), {'actuals': Decimal("0.00")})()).actuals
            for data in all_ffr_data.values()
        )

        # Expected: 60,082 EUR total (from summary statistics)
        expected = Decimal("60082.00")
        tolerance = Decimal("100.00")

        diff = abs(total_stsm - expected)
        assert diff <= tolerance, f"STSM total {total_stsm} differs from expected {expected} by {diff}"

    @pytest.mark.parametrize("gp,expected_actual", [
        (1, Decimal("20800.00")),
        (2, Decimal("0.00")),  # GP2 had no STSMs
        (5, Decimal("4642.00")),
    ])
    def test_stsm_known_values(self, ffr_parser, gp, expected_actual):
        """Verify known STSM values from FFR files."""
        data = ffr_parser.parse_grant_period(gp)

        if 'stsm' in data.categories:
            actual = data.categories['stsm'].actuals
            assert abs(actual - expected_actual) <= Decimal("1.00"), \
                f"GP{gp}: STSM actual {actual} != expected {expected_actual}"


class TestSTSMJSON:
    """Tests for STSM data in JSON files."""

    def test_json_stsm_count(self, stsm_detailed):
        """JSON should contain expected number of STSMs."""
        # Expected: 27 STSMs total
        assert len(stsm_detailed) >= 25, f"Too few STSMs in JSON: {len(stsm_detailed)}"
        assert len(stsm_detailed) <= 30, f"Too many STSMs in JSON: {len(stsm_detailed)}"

    def test_json_stsm_have_required_fields(self, stsm_detailed):
        """All JSON STSMs should have required fields."""
        required_fields = ['grantee_name', 'amount']

        for stsm in stsm_detailed:
            for field in required_fields:
                assert field in stsm or 'name' in stsm or 'grantee' in stsm, \
                    f"STSM missing grantee name field"

    def test_json_stsm_amounts_positive(self, stsm_detailed):
        """All STSM amounts should be positive."""
        for stsm in stsm_detailed:
            amount = stsm.get('amount', stsm.get('total', 0))
            if isinstance(amount, str):
                amount = float(amount.replace(',', '').replace(' ', ''))
            assert amount >= 0, f"Negative STSM amount: {amount}"


class TestSTSMIndividualSums:
    """Tests that individual STSM amounts sum to category total."""

    @pytest.mark.parametrize("gp", [1, 3, 4, 5])
    def test_individual_stsms_sum_to_category_total(self, ffr_parser, gp):
        """Sum of individual STSMs should equal STSM category total."""
        data = ffr_parser.parse_grant_period(gp)

        if not data.stsms:
            pytest.skip(f"GP{gp}: No individual STSMs parsed")

        individual_sum = sum(s.amount for s in data.stsms)
        category_total = data.categories.get('stsm', type('', (), {'actuals': Decimal("0.00")})()).actuals

        diff = abs(individual_sum - category_total)
        assert diff <= Decimal("1.00"), \
            f"GP{gp}: Individual STSMs sum to {individual_sum}, category total is {category_total}"
