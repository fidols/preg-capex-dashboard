import random
import pandas as pd

MONTHS = ["Jan 2026", "Feb 2026", "Mar 2026", "Apr 2026", "May 2026", "Jun 2026"]

_PROPERTIES = [
    {"name": "San Regis", "city": "Van Nuys", "state": "CA", "units": 390, "asset_type": "Affordable Conversion"},
    {"name": "Chaparral Apartments", "city": "Palmdale", "state": "CA", "units": 296, "asset_type": "Multifamily"},
    {"name": "The Marquee", "city": "Los Angeles", "state": "CA", "units": 236, "asset_type": "Multifamily"},
    {"name": "Avenues at Kennesaw", "city": "Kennesaw", "state": "GA", "units": 524, "asset_type": "Multifamily"},
    {"name": "Rosemont Peachtree Corners", "city": "Norcross", "state": "GA", "units": 440, "asset_type": "Multifamily"},
    {"name": "Valera Riverside", "city": "Lithia Springs", "state": "GA", "units": 425, "asset_type": "LIHTC"},
    {"name": "Tribute Verdae", "city": "Greenville", "state": "SC", "units": 268, "asset_type": "Affordable Conversion"},
    {"name": "The Paddock Club Columbia", "city": "Columbia", "state": "SC", "units": 336, "asset_type": "Bond Financed"},
    {"name": "Magnolia", "city": "Charleston", "state": "SC", "units": 312, "asset_type": "Multifamily"},
    {"name": "Viewcrest Village", "city": "Bremerton", "state": "WA", "units": 300, "asset_type": "LIHTC"},
    {"name": "Village at Broadstone Station", "city": "Apex", "state": "NC", "units": 300, "asset_type": "Multifamily"},
    {"name": "Inwood Crossing", "city": "Wichita", "state": "KS", "units": 260, "asset_type": "Multifamily"},
]


def generate_projects() -> pd.DataFrame:
    rng = random.Random(42)
    rows = []

    for p in _PROPERTIES:
        budget_per_unit = rng.uniform(6_000, 14_000)
        original_budget = round(p["units"] * budget_per_unit / 1_000) * 1_000

        pct_complete = round(rng.uniform(0.12, 0.88), 2)

        variance_factor = rng.uniform(0.93, 1.11)
        actual_spend = round(original_budget * pct_complete * variance_factor / 100) * 100

        num_cos = rng.randint(0, 3)
        co_amount = round(sum(rng.uniform(50_000, 220_000) for _ in range(num_cos)) / 100) * 100

        committed_costs = round(
            (actual_spend + (original_budget - actual_spend) * rng.uniform(0.55, 0.85)) / 100
        ) * 100
        committed_costs = min(committed_costs, original_budget + co_amount)

        cost_to_complete = max(original_budget + co_amount - actual_spend, 0)

        expected_spend = (original_budget + co_amount) * pct_complete
        variance_pct = round((actual_spend - expected_spend) / expected_spend, 4) if expected_spend > 0 else 0.0

        monthly_spend = _generate_monthly_spend(actual_spend, rng)

        rows.append({
            "project_name": p["name"],
            "city": p["city"],
            "state": p["state"],
            "units": p["units"],
            "asset_type": p["asset_type"],
            "original_budget": original_budget,
            "committed_costs": committed_costs,
            "actual_spend": actual_spend,
            "pct_complete": pct_complete,
            "change_orders_count": num_cos,
            "change_orders_amount": co_amount,
            "cost_to_complete": cost_to_complete,
            "variance_pct": variance_pct,
            "monthly_spend": monthly_spend,
        })

    return pd.DataFrame(rows)


def _generate_monthly_spend(total: float, rng: random.Random) -> list:
    weights = sorted([rng.uniform(0.08, 0.25) for _ in range(6)])
    total_weight = sum(weights)
    return [round(total * w / total_weight / 100) * 100 for w in weights]


def calculate_co_impact(df: pd.DataFrame, project_name: str, co_amount: float) -> tuple:
    row = df[df["project_name"] == project_name].iloc[0]
    new_ctc = row["cost_to_complete"] + co_amount
    new_budget = row["original_budget"] + row["change_orders_amount"] + co_amount
    expected_spend = new_budget * row["pct_complete"]
    new_variance = (row["actual_spend"] - expected_spend) / expected_spend if expected_spend > 0 else 0.0
    return new_ctc, round(new_variance, 4)
