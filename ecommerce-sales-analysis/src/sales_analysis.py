"""Summarize sales, products, countries, and customer purchasing behavior."""

from pathlib import Path
from typing import Any

import pandas as pd


def analyze_sales(data: pd.DataFrame) -> dict[str, Any]:
    """Calculate headline metrics and reusable analysis tables."""
    if data.empty:
        raise ValueError("There are no valid sales rows to analyze.")

    order_totals = data.groupby("InvoiceNo", as_index=False).agg(
        OrderRevenue=("Revenue", "sum"),
        OrderQuantity=("Quantity", "sum"),
    )
    identified_customers = data["CustomerID"].dropna()

    monthly_revenue = (
        data.groupby("Year_Month", as_index=False)
        .agg(Revenue=("Revenue", "sum"))
        .sort_values("Year_Month")
    )
    daily_sales = (
        data.assign(SaleDate=data["InvoiceDate"].dt.normalize())
        .groupby("SaleDate", as_index=False)
        .agg(Revenue=("Revenue", "sum"), Orders=("InvoiceNo", "nunique"))
        .sort_values("SaleDate")
    )

    product_sales = data.groupby(
        ["StockCode", "Description"], as_index=False, dropna=False
    ).agg(
        Revenue=("Revenue", "sum"),
        Quantity=("Quantity", "sum"),
        Orders=("InvoiceNo", "nunique"),
    )
    top_products_by_revenue = product_sales.sort_values(
        "Revenue", ascending=False
    ).head(10)
    top_products_by_quantity = product_sales.sort_values(
        "Quantity", ascending=False
    ).head(10)

    country_revenue = (
        data.groupby("Country", as_index=False)
        .agg(
            Revenue=("Revenue", "sum"),
            Orders=("InvoiceNo", "nunique"),
            Customers=("CustomerID", "nunique"),
            Quantity=("Quantity", "sum"),
        )
        .sort_values("Revenue", ascending=False)
    )
    monthly_orders = (
        data.groupby("Year_Month", as_index=False)
        .agg(Orders=("InvoiceNo", "nunique"))
        .sort_values("Year_Month")
    )

    customer_orders = data.dropna(subset=["CustomerID"]).groupby(
        ["CustomerID", "InvoiceNo"], as_index=False
    ).agg(
        OrderRevenue=("Revenue", "sum"),
        OrderQuantity=("Quantity", "sum"),
        OrderDate=("InvoiceDate", "min"),
    )
    customer_summary = (
        customer_orders.groupby("CustomerID", as_index=False)
        .agg(
            Orders=("InvoiceNo", "nunique"),
            TotalRevenue=("OrderRevenue", "sum"),
            AverageOrderValue=("OrderRevenue", "mean"),
            TotalQuantity=("OrderQuantity", "sum"),
            FirstOrder=("OrderDate", "min"),
            LastOrder=("OrderDate", "max"),
        )
        .sort_values("TotalRevenue", ascending=False)
    )

    metrics = {
        "total_revenue": float(data["Revenue"].sum()),
        "total_orders": int(data["InvoiceNo"].nunique()),
        "total_unique_customers": int(identified_customers.nunique()),
        "average_order_value": float(order_totals["OrderRevenue"].mean()),
        "total_quantity_sold": float(data["Quantity"].sum()),
        "transactions_analyzed": int(len(data)),
    }

    return {
        "metrics": metrics,
        "monthly_revenue": monthly_revenue,
        "daily_sales": daily_sales,
        "top_products_by_revenue": top_products_by_revenue,
        "top_products_by_quantity": top_products_by_quantity,
        "country_revenue": country_revenue,
        "monthly_orders": monthly_orders,
        "customer_summary": customer_summary,
    }


def save_analysis_reports(
    results: dict[str, Any], reports_directory: str | Path
) -> None:
    """Write analysis tables and headline metrics to CSV files."""
    reports_path = Path(reports_directory)
    reports_path.mkdir(parents=True, exist_ok=True)

    report_tables = {
        "monthly_revenue": results["monthly_revenue"],
        "daily_sales": results["daily_sales"],
        "top_products_by_revenue": results["top_products_by_revenue"],
        "top_products_by_quantity": results["top_products_by_quantity"],
        "country_revenue": results["country_revenue"],
        "monthly_orders": results["monthly_orders"],
        "customer_summary": results["customer_summary"],
    }
    for report_name, table in report_tables.items():
        table.to_csv(reports_path / f"{report_name}.csv", index=False)

    pd.DataFrame([results["metrics"]]).to_csv(
        reports_path / "summary_metrics.csv", index=False
    )


def _format_pounds(value: float) -> str:
    """Format a numeric value as pounds sterling."""
    return f"£{value:,.2f}"


def generate_business_insights(
    results: dict[str, Any], reports_directory: str | Path
) -> str:
    """Create evidence-based observations and save them as a text report."""
    monthly_revenue = results["monthly_revenue"]
    top_products = results["top_products_by_revenue"]
    countries = results["country_revenue"]
    customer_summary = results["customer_summary"]
    metrics = results["metrics"]

    if monthly_revenue.empty or top_products.empty or countries.empty:
        raise ValueError("Business insights cannot be generated from empty summaries.")

    highest_month = monthly_revenue.loc[monthly_revenue["Revenue"].idxmax()]
    lowest_month = monthly_revenue.loc[monthly_revenue["Revenue"].idxmin()]
    monthly_changes = monthly_revenue["Revenue"].diff().dropna()
    revenue_increases = int((monthly_changes > 0).sum())
    revenue_decreases = int((monthly_changes < 0).sum())
    unchanged_months = int((monthly_changes == 0).sum())
    leading_country = countries.iloc[0]
    top_product_lines = [
        f"- {row.Description} (stock code {row.StockCode}): "
        f"{_format_pounds(row.Revenue)}"
        for row in top_products.head(5).itertuples(index=False)
    ]

    identifiable_customers = len(customer_summary)
    repeat_customers = int((customer_summary["Orders"] > 1).sum())
    repeat_customer_share = (
        repeat_customers / identifiable_customers * 100
        if identifiable_customers
        else 0.0
    )
    month_count = len(monthly_revenue)

    lines = [
        "E-Commerce Sales Analysis: Business Insights",
        "=" * 47,
        "",
        "Scope and interpretation",
        "------------------------",
        (
            "These findings are calculated from cleaned positive-quantity sales. "
            "Cancellation invoices and rows with non-positive quantities or prices "
            "were excluded; returns are not netted against sales."
        ),
        (
            "Customer counts and repeat-purchase metrics include only transactions "
            "with a recorded CustomerID. Missing IDs remain in sales totals."
        ),
        "All amounts are reported in the dataset's stated currency (£).",
        "",
        "Observed findings",
        "-----------------",
        (
            f"- Total revenue: {_format_pounds(metrics['total_revenue'])}; "
            f"{metrics['total_orders']:,} orders; "
            f"{metrics['total_unique_customers']:,} identified customers."
        ),
        (
            f"- Highest-revenue month: {highest_month['Year_Month']} "
            f"({_format_pounds(highest_month['Revenue'])})."
        ),
        (
            f"- Lowest-revenue month: {lowest_month['Year_Month']} "
            f"({_format_pounds(lowest_month['Revenue'])})."
        ),
        "- Top products by revenue:",
        *top_product_lines,
        (
            f"- Highest-revenue country: {leading_country['Country']} "
            f"({_format_pounds(leading_country['Revenue'])})."
        ),
        (
            f"- Monthly revenue spans {month_count} month(s). "
            f"Across {len(monthly_changes)} consecutive-month comparisons, "
            f"revenue increased {revenue_increases} time(s), decreased "
            f"{revenue_decreases} time(s), and was unchanged "
            f"{unchanged_months} time(s). See monthly_revenue.csv and the "
            "monthly revenue chart for the full series. Partial months can "
            "affect these comparisons, and this dataset alone does not "
            "establish a recurring seasonal trend."
        ),
        (
            f"- Among customers with an ID, {repeat_customers:,} of "
            f"{identifiable_customers:,} placed more than one order "
            f"({repeat_customer_share:.1f}%)."
        ),
        "",
        "Recommendations to consider",
        "----------------------------",
        (
            "- Review the highest-revenue products for stock availability and "
            "merchandising opportunities. Revenue is not profit, so check margins "
            "and inventory costs before making stock decisions."
        ),
        (
            "- Investigate the lowest-revenue month alongside promotions, opening "
            "days, and whether the month is only partially represented before "
            "planning campaigns."
        ),
        (
            "- Compare country-level revenue with shipping costs, taxes, and "
            "margins before prioritizing geographic expansion."
        ),
        (
            "- Consider testing customer-retention ideas, then measure their "
            "results against a suitable baseline; the observed repeat-order share "
            "does not show what caused customers to return."
        ),
        "",
        (
            "These recommendations are hypotheses for further investigation. "
            "Aggregated transaction patterns show associations, not causation."
        ),
    ]

    report = "\n".join(lines) + "\n"
    reports_path = Path(reports_directory)
    reports_path.mkdir(parents=True, exist_ok=True)
    (reports_path / "business_insights.txt").write_text(report, encoding="utf-8")
    return report
