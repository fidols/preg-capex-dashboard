# tests/test_projects.py
import pytest
import pandas as pd
from data.projects import generate_projects, MONTHS, calculate_co_impact

REQUIRED_COLUMNS = [
    "project_name", "city", "state", "units", "asset_type",
    "original_budget", "committed_costs", "actual_spend",
    "pct_complete", "change_orders_count", "change_orders_amount",
    "cost_to_complete", "variance_pct", "monthly_spend",
]


def test_generate_projects_returns_dataframe():
    df = generate_projects()
    assert isinstance(df, pd.DataFrame)


def test_generate_projects_has_12_rows():
    df = generate_projects()
    assert len(df) == 12


def test_generate_projects_has_required_columns():
    df = generate_projects()
    for col in REQUIRED_COLUMNS:
        assert col in df.columns, f"Missing column: {col}"


def test_generate_projects_is_deterministic():
    df1 = generate_projects()
    df2 = generate_projects()
    pd.testing.assert_frame_equal(df1, df2)


def test_budgets_are_positive():
    df = generate_projects()
    assert (df["original_budget"] > 0).all()


def test_actual_spend_does_not_exceed_budget_by_more_than_20_pct():
    df = generate_projects()
    ratio = df["actual_spend"] / df["original_budget"]
    assert (ratio < 1.20).all()


def test_pct_complete_is_between_0_and_1():
    df = generate_projects()
    assert (df["pct_complete"] >= 0).all()
    assert (df["pct_complete"] <= 1).all()


def test_monthly_spend_has_6_values_per_project():
    df = generate_projects()
    for _, row in df.iterrows():
        assert len(row["monthly_spend"]) == 6


def test_months_has_6_entries():
    assert len(MONTHS) == 6


def test_calculate_co_impact_increases_cost_to_complete():
    df = generate_projects()
    project = df["project_name"].iloc[0]
    original_ctc = df.loc[df["project_name"] == project, "cost_to_complete"].iloc[0]
    new_ctc, new_variance = calculate_co_impact(df, project, 100_000)
    assert new_ctc == original_ctc + 100_000


def test_calculate_co_impact_with_zero_amount_is_unchanged():
    df = generate_projects()
    project = df["project_name"].iloc[0]
    original_ctc = df.loc[df["project_name"] == project, "cost_to_complete"].iloc[0]
    new_ctc, _ = calculate_co_impact(df, project, 0)
    assert new_ctc == original_ctc
