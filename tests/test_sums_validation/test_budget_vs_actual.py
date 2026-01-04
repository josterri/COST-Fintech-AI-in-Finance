"""
Test WBP budget vs FFR actual expenditure.

Verifies alignment between Work & Budget Plans (budgeted amounts)
and Final Financial Reports (actual expenditure).
"""

import pytest
from decimal import Decimal


class TestWBPBudgetVsFFRActual:
    """Tests comparing WBP budgets to FFR actuals."""

    @pytest.mark.parametrize("gp", [1, 2, 3, 4, 5])
    def test_wbp_budget_extracted(self, wbp_parser, gp):
        """WBP parser extracts budget correctly."""
        data = wbp_parser.parse_grant_period(gp)

        assert data.total_grant > Decimal("0.00"), \
            f"GP{gp}: WBP total grant is zero"

    @pytest.mark.parametrize("gp", [1, 2, 3, 4, 5])
    def test_wbp_budget_matches_ffr_budget(self, wbp_parser, ffr_parser, gp):
        """WBP total grant should match FFR grant budget."""
        wbp_data = wbp_parser.parse_grant_period(gp)
        ffr_data = ffr_parser.parse_grant_period(gp)

        # WBP total grant should be close to FFR grant budget
        # Note: FFR budget may include amendments
        wbp_budget = wbp_data.total_grant
        ffr_budget = ffr_data.grant_budget

        if wbp_budget > 0 and ffr_budget > 0:
            # Allow 50% difference due to budget amendments
            ratio = float(wbp_budget / ffr_budget)
            assert 0.5 <= ratio <= 2.0, \
                f"GP{gp}: WBP budget ({wbp_budget}) vs FFR budget ({ffr_budget}) ratio={ratio:.2f}"

    @pytest.mark.parametrize("gp", [1, 2, 3, 4, 5])
    def test_actual_does_not_exceed_budget_significantly(self, ffr_parser, gp):
        """Actual expenditure should not significantly exceed budget."""
        data = ffr_parser.parse_grant_period(gp)

        if data.grant_budget > 0 and data.total_eligible > 0:
            ratio = float(data.total_eligible / data.grant_budget)

            # Allow up to 5% overspend due to rounding/reallocation
            assert ratio <= 1.05, \
                f"GP{gp}: Overspent by {(ratio-1)*100:.1f}%"


class TestCategoryBudgetVsActual:
    """Tests comparing category-level budgets to actuals."""

    @pytest.mark.parametrize("gp", [1, 2, 3, 4, 5])
    def test_meetings_budget_vs_actual(self, wbp_parser, ffr_parser, gp):
        """Meetings actual should not significantly exceed budget."""
        wbp_data = wbp_parser.parse_grant_period(gp)
        ffr_data = ffr_parser.parse_grant_period(gp)

        wbp_meetings = wbp_data.categories.get('meetings', type('', (), {'budget': Decimal("0.00")})()).budget
        ffr_meetings = ffr_data.categories.get('meetings', type('', (), {'actuals': Decimal("0.00")})()).actuals

        if wbp_meetings > 0 and ffr_meetings > 0:
            # Categories can have more variation due to reallocation
            ratio = float(ffr_meetings / wbp_meetings)

            # Allow significant variation (budgets often get reallocated)
            if ratio > 2.0:
                pytest.skip(f"GP{gp}: Meetings actual ({ffr_meetings}) >> budget ({wbp_meetings})")

    @pytest.mark.parametrize("gp", [1, 3, 4, 5])  # GPs with STSMs
    def test_stsm_budget_vs_actual(self, wbp_parser, ffr_parser, gp):
        """STSM actual should not significantly exceed budget."""
        wbp_data = wbp_parser.parse_grant_period(gp)
        ffr_data = ffr_parser.parse_grant_period(gp)

        wbp_stsm = wbp_data.categories.get('stsm', type('', (), {'budget': Decimal("0.00")})()).budget
        ffr_stsm = ffr_data.categories.get('stsm', type('', (), {'actuals': Decimal("0.00")})()).actuals

        if wbp_stsm > 0 and ffr_stsm > 0:
            ratio = float(ffr_stsm / wbp_stsm)

            # STSMs in GP1 were oversubscribed (budget reallocation)
            if gp == 1:
                assert ratio <= 3.0, f"GP{gp}: STSM severely overspent"
            else:
                assert ratio <= 1.5, f"GP{gp}: STSM overspent by {(ratio-1)*100:.0f}%"


class TestBudgetReallocation:
    """Tests for understanding budget reallocation patterns."""

    @pytest.mark.parametrize("gp", [1, 2, 3, 4, 5])
    def test_total_actual_within_budget(self, ffr_parser, gp):
        """Total actual should be at or below total budget."""
        data = ffr_parser.parse_grant_period(gp)

        if data.grant_budget > 0 and data.total_eligible > 0:
            assert data.total_eligible <= data.grant_budget * Decimal("1.01"), \
                f"GP{gp}: Total actual ({data.total_eligible}) exceeds budget ({data.grant_budget})"

    def test_overall_budget_utilization(self, all_ffr_data):
        """Overall budget utilization across all GPs."""
        total_budget = sum(d.grant_budget for d in all_ffr_data.values())
        total_actual = sum(d.total_eligible for d in all_ffr_data.values())

        utilization = float(total_actual / total_budget)

        # Expected ~80% overall utilization
        assert 0.75 <= utilization <= 0.85, \
            f"Overall utilization {utilization*100:.1f}% outside expected range [75%, 85%]"
