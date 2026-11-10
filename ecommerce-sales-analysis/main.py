"""Run the complete e-commerce sales analysis from the project root."""

from pathlib import Path

from src.data_cleaning import clean_data
from src.data_loader import DEFAULT_DATASET_PATH, inspect_data, load_data
from src.sales_analysis import (
    analyze_sales,
    generate_business_insights,
    save_analysis_reports,
)
from src.visualization import create_visualizations


PROJECT_ROOT = Path(__file__).resolve().parent
CHARTS_DIRECTORY = PROJECT_ROOT / "outputs" / "charts"
REPORTS_DIRECTORY = PROJECT_ROOT / "outputs" / "reports"


def main() -> int:
    """Run each project stage in order and return an exit status."""
    print("E-Commerce Sales Analysis")
    print("=========================")
    print(f"Dataset: {DEFAULT_DATASET_PATH}")

    try:
        original_data = load_data()
        inspect_data(original_data)

        cleaned_data, cleaning_log = clean_data(original_data)
        results = analyze_sales(cleaned_data)
        save_analysis_reports(results, REPORTS_DIRECTORY)
        charts = create_visualizations(results, CHARTS_DIRECTORY)
        insights = generate_business_insights(results, REPORTS_DIRECTORY)
    except (FileNotFoundError, ImportError, RuntimeError, ValueError) as error:
        print(f"\nAnalysis could not be completed: {error}")
        return 1

    metrics = results["metrics"]
    print("\nKey metrics:")
    print(f"  Total revenue: £{metrics['total_revenue']:,.2f}")
    print(f"  Orders: {metrics['total_orders']:,}")
    print(f"  Identified customers: {metrics['total_unique_customers']:,}")
    print(f"  Average order value: £{metrics['average_order_value']:,.2f}")
    print(f"  Quantity sold: {metrics['total_quantity_sold']:,.0f}")
    print(
        "  Rows retained: "
        f"{cleaning_log['rows_after_cleaning']:,} of "
        f"{cleaning_log['rows_before_cleaning']:,}"
    )
    print(f"\nSaved {len(charts)} charts to {CHARTS_DIRECTORY}")
    print(f"Saved analysis reports to {REPORTS_DIRECTORY}")
    print("\nBusiness insights preview:")
    print("\n".join(insights.splitlines()[11:17]))
    print("\nAnalysis completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
