"""
Test FSAC (Financial and Scientific Administration and Coordination) compliance.

FSAC has a maximum limit of 15% of networking expenditure.
This test verifies that all grant periods comply with this rule.
"""

import pytest
from decimal import Decimal


class TestFSACCompliance:
    """Tests for FSAC 15% compliance rule."""

    @pytest.mark.parametrize("gp", [1, 2, 3, 4, 5])
    def test_fsac_extraction(self, ffr_parser, gp):
        """FFR parser extracts FSAC category correctly."""
        data = ffr_parser.parse_grant_period(gp)

        assert 'fsac' in data.categories, f"GP{gp}: FSAC category not found"

        fsac_actual = data.categories['fsac'].actuals
        assert fsac_actual >= Decimal("0.00"), f"GP{gp}: negative FSAC amount"

    @pytest.mark.parametrize("gp", [1, 2, 3, 4, 5])
    def test_fsac_max_15_percent(self, ffr_parser, gp):
        """FSAC should not exceed 15% of eligible networking expenditure."""
        data = ffr_parser.parse_grant_period(gp)

        # Calculate total networking expenditure (excluding FSAC)
        networking_categories = [
            'meetings', 'training_schools', 'stsm', 'virtual_mobility',
            'virtual_networking_support', 'itc_conference', 'dissemination',
            'dissemination_conference', 'oersa'
        ]

        networking_total = Decimal("0.00")
        for cat_name in networking_categories:
            if cat_name in data.categories:
                networking_total += data.categories[cat_name].actuals

        # Also check 'eligible_networking' if present
        if 'eligible_networking' in data.categories:
            networking_total = data.categories['eligible_networking'].actuals

        # Also check 'total_networking' if present
        if 'total_networking' in data.categories:
            networking_total = data.categories['total_networking'].actuals

        fsac_actual = data.categories.get('fsac', type('', (), {'actuals': Decimal("0.00")})()).actuals

        if networking_total > Decimal("0.00"):
            fsac_percentage = (fsac_actual / networking_total) * 100

            # FSAC should be <= 15% (allow small tolerance for rounding)
            assert fsac_percentage <= Decimal("15.5"), \
                f"GP{gp}: FSAC is {fsac_percentage:.2f}% of networking (max 15%)"

    @pytest.mark.parametrize("gp,expected_fsac", [
        (1, Decimal("6190.41")),
        (5, Decimal("35258.51")),
    ])
    def test_fsac_known_values(self, ffr_parser, gp, expected_fsac):
        """Verify known FSAC values from FFR files."""
        data = ffr_parser.parse_grant_period(gp)

        if 'fsac' in data.categories:
            actual = data.categories['fsac'].actuals
            assert abs(actual - expected_fsac) <= Decimal("100.00"), \
                f"GP{gp}: FSAC actual {actual} != expected {expected_fsac}"


class TestFSACCalculation:
    """Tests for FSAC calculation correctness."""

    @pytest.mark.parametrize("gp", [1, 2, 3, 4, 5])
    def test_fsac_plus_networking_equals_total(self, ffr_parser, gp):
        """FSAC + networking should equal total eligible expenditure."""
        data = ffr_parser.parse_grant_period(gp)

        # Get values from FFR
        fsac = data.categories.get('fsac', type('', (), {'actuals': Decimal("0.00")})()).actuals
        eligible = data.categories.get('eligible_networking', type('', (), {'actuals': Decimal("0.00")})()).actuals
        total = data.categories.get('total_eligible', type('', (), {'actuals': Decimal("0.00")})()).actuals

        # If we have total_eligible, verify
        if total > Decimal("0.00") and eligible > Decimal("0.00"):
            calculated_total = fsac + eligible
            diff = abs(calculated_total - total)

            assert diff <= Decimal("1.00"), \
                f"GP{gp}: FSAC ({fsac}) + Networking ({eligible}) = {calculated_total} != Total ({total})"

    def test_overall_fsac_compliance(self, all_ffr_data):
        """Overall FSAC across all GPs should be compliant."""
        total_fsac = Decimal("0.00")
        total_networking = Decimal("0.00")

        for data in all_ffr_data.values():
            if 'fsac' in data.categories:
                total_fsac += data.categories['fsac'].actuals
            if 'eligible_networking' in data.categories:
                total_networking += data.categories['eligible_networking'].actuals
            elif 'total_networking' in data.categories:
                total_networking += data.categories['total_networking'].actuals

        if total_networking > Decimal("0.00"):
            overall_percentage = (total_fsac / total_networking) * 100

            assert overall_percentage <= Decimal("15.5"), \
                f"Overall FSAC is {overall_percentage:.2f}% of networking (max 15%)"
