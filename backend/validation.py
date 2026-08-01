"""
Stage 6: Input validation.

Two layers:
1. Hard validation (used by Pydantic in main.py) - rejects genuinely
   invalid input like negative numbers, before any computation happens.
2. Soft warnings (this file's `check_warnings`) - the numbers are valid
   and get analyzed, but something about them looks unusual enough that
   the user should know before trusting the AI's read on it.
"""


def check_warnings(data: dict) -> list[str]:
    """
    Looks at raw financial inputs (before ratios are computed) and flags
    combinations that are technically valid but likely to indicate either
    a data entry mistake or a genuinely unusual financial position.
    Returns a list of plain-language warning strings (empty if none).
    """
    warnings = []

    revenue = data["revenue"]
    cogs = data["cost_of_goods_sold"]
    net_income = data["net_income"]
    current_assets = data["current_assets"]
    current_liabilities = data["current_liabilities"]
    inventory = data["inventory"]
    total_assets = data["total_assets"]
    total_liabilities = data["total_liabilities"]
    total_equity = data["total_equity"]

    if revenue == 0 and cogs > 0:
        warnings.append(
            "Revenue is zero but cost of goods sold is not — double check these figures."
        )

    if cogs > revenue and revenue > 0:
        warnings.append(
            "Cost of goods sold is higher than revenue — this means a negative gross margin. "
            "Possible for a struggling business, but worth confirming the numbers are right."
        )

    if inventory > current_assets:
        warnings.append(
            "Inventory is larger than total current assets — inventory is usually a subset "
            "of current assets, so this combination is unusual."
        )

    if total_liabilities > total_assets:
        warnings.append(
            "Total liabilities exceed total assets — this implies negative equity. "
            "Possible in a struggling business, but confirm the numbers are accurate."
        )

    if abs(total_assets - (total_liabilities + total_equity)) > max(1, total_assets * 0.01):
        warnings.append(
            "Total assets don't roughly equal total liabilities + total equity — "
            "in real accounting these should balance. Double check your figures."
        )

    if net_income > revenue and revenue > 0:
        warnings.append(
            "Net income is higher than revenue — that's not possible in normal accounting. "
            "Double check these figures."
        )

    if current_liabilities == 0 and current_assets > 0:
        warnings.append(
            "Current liabilities are zero — unusual for most businesses. "
            "Current ratio and quick ratio will be undefined."
        )

    return warnings