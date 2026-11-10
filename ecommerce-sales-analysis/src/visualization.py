"""Create and save charts for the sales analysis."""

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import pandas as pd
import seaborn as sns


def _pound_axis(value: float, _position: int) -> str:
    return f"£{value:,.0f}"


def _save_horizontal_bar_chart(
    data: pd.DataFrame,
    value_column: str,
    label_column: str,
    title: str,
    filename: str,
    charts_directory: Path,
) -> None:
    chart_data = data.sort_values(value_column, ascending=True)
    figure_height = max(5, 0.38 * len(chart_data))
    figure, axis = plt.subplots(figsize=(11, figure_height))
    sns.barplot(
        data=chart_data,
        x=value_column,
        y=label_column,
        hue=label_column,
        palette="Blues_r",
        legend=False,
        ax=axis,
    )
    axis.set_title(title, fontsize=15, pad=14)
    if value_column == "Revenue":
        axis.set_xlabel("Revenue (£)")
    elif value_column == "Quantity":
        axis.set_xlabel("Quantity sold (units)")
    else:
        axis.set_xlabel(value_column)
    axis.set_ylabel("")
    if value_column == "Revenue":
        axis.xaxis.set_major_formatter(FuncFormatter(_pound_axis))
    figure.tight_layout()
    figure.savefig(charts_directory / filename, dpi=160, bbox_inches="tight")
    plt.close(figure)


def create_visualizations(
    results: dict[str, Any], charts_directory: str | Path
) -> list[Path]:
    """Save all project charts and return their file paths."""
    charts_path = Path(charts_directory)
    charts_path.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", context="notebook")
    created_charts: list[Path] = []

    monthly_revenue = results["monthly_revenue"]
    figure, axis = plt.subplots(figsize=(12, 6))
    sns.lineplot(
        data=monthly_revenue,
        x="Year_Month",
        y="Revenue",
        marker="o",
        linewidth=2,
        color="#2364AA",
        ax=axis,
    )
    axis.set_title("Monthly Revenue Trend", fontsize=15, pad=14)
    axis.set_xlabel("Month")
    axis.set_ylabel("Revenue (£)")
    axis.yaxis.set_major_formatter(FuncFormatter(_pound_axis))
    axis.tick_params(axis="x", rotation=45)
    figure.tight_layout()
    monthly_chart = charts_path / "monthly_revenue_trend.png"
    figure.savefig(monthly_chart, dpi=160, bbox_inches="tight")
    plt.close(figure)
    created_charts.append(monthly_chart)

    products = results["top_products_by_revenue"].copy()
    products["Product"] = (
        products["Description"].astype(str).str.slice(0, 40)
        + " ("
        + products["StockCode"].astype(str)
        + ")"
    )
    product_revenue_chart = charts_path / "top_10_products_by_revenue.png"
    _save_horizontal_bar_chart(
        products,
        "Revenue",
        "Product",
        "Top 10 Products by Revenue",
        product_revenue_chart.name,
        charts_path,
    )
    created_charts.append(product_revenue_chart)

    quantity_products = results["top_products_by_quantity"].copy()
    quantity_products["Product"] = (
        quantity_products["Description"].astype(str).str.slice(0, 40)
        + " ("
        + quantity_products["StockCode"].astype(str)
        + ")"
    )
    product_quantity_chart = charts_path / "top_10_products_by_quantity.png"
    _save_horizontal_bar_chart(
        quantity_products,
        "Quantity",
        "Product",
        "Top 10 Products by Quantity Sold",
        product_quantity_chart.name,
        charts_path,
    )
    created_charts.append(product_quantity_chart)

    top_countries = results["country_revenue"].head(10)
    top_countries_chart = charts_path / "top_10_countries_by_revenue.png"
    _save_horizontal_bar_chart(
        top_countries,
        "Revenue",
        "Country",
        "Top 10 Countries by Revenue",
        top_countries_chart.name,
        charts_path,
    )
    created_charts.append(top_countries_chart)

    monthly_orders = results["monthly_orders"]
    figure, axis = plt.subplots(figsize=(12, 6))
    sns.lineplot(
        data=monthly_orders,
        x="Year_Month",
        y="Orders",
        marker="o",
        linewidth=2,
        color="#2A9D8F",
        ax=axis,
    )
    axis.set_title("Monthly Order Trends", fontsize=15, pad=14)
    axis.set_xlabel("Month")
    axis.set_ylabel("Number of Orders")
    axis.tick_params(axis="x", rotation=45)
    figure.tight_layout()
    orders_chart = charts_path / "monthly_order_trends.png"
    figure.savefig(orders_chart, dpi=160, bbox_inches="tight")
    plt.close(figure)
    created_charts.append(orders_chart)

    figure, axis = plt.subplots(figsize=(10, 6))
    sns.histplot(
        data=results["daily_sales"],
        x="Revenue",
        bins=30,
        color="#E76F51",
        edgecolor="white",
        ax=axis,
    )
    axis.set_title("Daily Revenue Distribution", fontsize=15, pad=14)
    axis.set_xlabel("Daily revenue (£)")
    axis.set_ylabel("Number of days")
    axis.xaxis.set_major_formatter(FuncFormatter(_pound_axis))
    figure.tight_layout()
    distribution_chart = charts_path / "revenue_distribution.png"
    figure.savefig(distribution_chart, dpi=160, bbox_inches="tight")
    plt.close(figure)
    created_charts.append(distribution_chart)

    country_comparison_chart = charts_path / "sales_by_country.png"
    _save_horizontal_bar_chart(
        results["country_revenue"].head(15),
        "Revenue",
        "Country",
        "Revenue by Country (Top 15)",
        country_comparison_chart.name,
        charts_path,
    )
    created_charts.append(country_comparison_chart)

    return created_charts
