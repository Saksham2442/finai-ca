"""
Pure ratio calculation logic, kept separate from the API layer.
Why separate: you can test and trust this file completely on its own,
without needing a server running or FastAPI installed.
"""


def safe_div(a, b):
    return round(a / b, 4) if b else None


def compute_ratios(data: dict) -> dict:
    revenue = data["revenue"]
    cogs = data["cost_of_goods_sold"]
    net_income = data["net_income"]
    current_assets = data["current_assets"]
    current_liabilities = data["current_liabilities"]
    inventory = data["inventory"]
    total_assets = data["total_assets"]
    total_liabilities = data["total_liabilities"]
    total_equity = data["total_equity"]

    return {
        "gross_margin": safe_div(revenue - cogs, revenue),
        "net_margin": safe_div(net_income, revenue),
        "current_ratio": safe_div(current_assets, current_liabilities),
        "quick_ratio": safe_div(current_assets - inventory, current_liabilities),
        "debt_to_equity": safe_div(total_liabilities, total_equity),
        "return_on_assets": safe_div(net_income, total_assets),
    }