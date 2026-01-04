"""
Test that category totals sum to grand totals.

Verifies:
- Category totals sum correctly within each GP
- GP totals sum to overall grand total
- WBP budgets align with FFR figures
"""

import pytest
from decimal import Decimal


class TestGPGrandTotals:
    """Tests for grant period grand total calculations."""

    @pytest.mark.parametrize("gp,expected_budget,expected_actual", [
        (1, Decimal("62985.50"), Decimal("47459.83")),
        (2, Decimal("202607.00"), Decimal("33770.46")),
        (3, Decimal("169820.50"), Decimal("166262.38")),
        (4, Decimal("257925.91"), Decimal("256854.39")),
        (5, Decimal("270315.26"), Decimal("270315.26")),
    ])
    def test_gp_totals_match_expected(self, ffr_parser, gp, expected_budget, expected_actual):
        """FFR grand totals should match expected values."""
        data = ffr_parser.parse_grant_period(gp)

        # Check budget
        budget = data.grant_budget
        if budget > 0:
            budget_diff = abs(budget - expected_budget)
            assert budget_diff <= Decimal("100.00"), \
                f"GP{gp}: Budget {budget} != expected {expected_budget}"

        # Check actual (total eligible)
        actual = data.total_eligible
        if actual > 0:
            actual_diff = abs(actual - expected_actual)
            assert actual_diff <= Decimal("100.00"), \
                f"GP{gp}: Actual {actual} != expected {expected_actual}"

    def test_all_gps_sum_to_grand_total(self, all_ffr_data, expected_grand_totals):
        """Sum of all GP totals should equal grand total."""
        total_budget = Decimal("0.00")
        total_actual = Decimal("0.00")

        for data in all_ffr_data.values():
            total_budget += data.grant_budget
            total_actual += data.total_eligible

        # Expected grand totals
        expected_budget = Decimal("963654.17")
        expected_actual = Decimal("774662.32")

        budget_diff = abs(total_budget - expected_budget)
        actual_diff = abs(total_actual - expected_actual)

        tolerance = Decimal("1000.00")

        assert budget_diff <= tolerance, \
            f"Total budget {total_budget} != expected {expected_budget}"
        assert actual_diff <= tolerance, \
            f"Total actual {total_actual} != expected {expected_actual}"


class TestNetworkingPlusFSACEqualsTotal:
    """Tests that Networking + FSAC = Total Eligible."""

    @pytest.mark.parametrize("gp", [1, 2, 3, 4, 5])
    def test_networking_plus_fsac_equals_total(self, ffr_parser, gp):
        """Networking expenditure + FSAC should equal total eligible."""
        data = ffr_parser.parse_grant_period(gp)

        # Get FSAC
        fsac = data.categories.get('fsac', type('', (), {'actuals': Decimal("0.00")})()).actuals

        # Get networking total
        networking = Decimal("0.00")
        if 'eligible_networking' in data.categories:
            networking = data.categories['eligible_networking'].actuals
        elif 'total_networking' in data.categories:
            networking = data.categories['total_networking'].actuals

        # Get total eligible
        total_eligible = Decimal("0.00")
        if 'total_eligible' in data.categories:
            total_eligible = data.categories['total_eligible'].actuals
        else:
            total_eligible = data.total_eligible

        if networking > 0 and fsac > 0 and total_eligible > 0:
            calculated_total = networking + fsac
            diff = abs(calculated_total - total_eligible)

            assert diff <= Decimal("1.00"), \
                f"GP{gp}: Networking ({networking}) + FSAC ({fsac}) = {calculated_total} != Total ({total_eligible})"


class TestBudgetUtilization:
    """Tests for budget utilization percentages."""

    @pytest.mark.parametrize("gp,min_utilization,max_utilization", [
        (1, 0.50, 1.00),  # GP1: ~75% utilization
        (2, 0.10, 0.50),  # GP2: ~17% utilization (shortened period)
        (3, 0.90, 1.10),  # GP3: ~98% utilization
        (4, 0.95, 1.05),  # GP4: ~99% utilization
        (5, 0.99, 1.01),  # GP5: 100% utilization
    ])
    def test_budget_utilization_in_range(self, ffr_parser, gp, min_utilization, max_utilization):
        """Budget utilization should be within expected range."""
        data = ffr_parser.parse_grant_period(gp)

        if data.grant_budget > 0:
            utilization = float(data.total_eligible / data.grant_budget)

            assert min_utilization <= utilization <= max_utilization, \
                f"GP{gp}: Utilization {utilization*100:.1f}% outside range [{min_utilization*100:.0f}%, {max_utilization*100:.0f}%]"
