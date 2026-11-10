"""Clean retail transactions while preserving the original input DataFrame."""

import pandas as pd


EXPECTED_COLUMNS = {
    "invoiceno": "InvoiceNo",
    "stockcode": "StockCode",
    "description": "Description",
    "quantity": "Quantity",
    "invoicedate": "InvoiceDate",
    "unitprice": "UnitPrice",
    "customerid": "CustomerID",
    "country": "Country",
}


def clean_data(data: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """Return cleaned sales transactions and a count of each cleaning decision.

    Cancellation invoices and non-positive quantities are excluded from sales
    metrics, so returns are not presented as positive sales or netted against
    purchases. The input DataFrame is copied and is never changed in place.
    """
    cleaned = data.copy()
    initial_rows = len(cleaned)

    # Normalize headers so harmless differences in spacing or capitalization
    # do not prevent the known UCI fields from being recognized.
    cleaned.columns = [
        EXPECTED_COLUMNS.get(
            str(column).strip().lower().replace(" ", "").replace("_", ""),
            str(column).strip(),
        )
        for column in cleaned.columns
    ]

    required_columns = [
        "InvoiceNo",
        "StockCode",
        "Quantity",
        "InvoiceDate",
        "UnitPrice",
    ]
    missing_columns = [column for column in required_columns if column not in cleaned.columns]
    if missing_columns:
        raise ValueError(
            "The workbook is missing required columns: " + ", ".join(missing_columns)
        )

    for optional_column in ("Description", "CustomerID", "Country"):
        if optional_column not in cleaned.columns:
            cleaned[optional_column] = pd.NA

    cleaned["InvoiceNo"] = cleaned["InvoiceNo"].astype("string").str.strip()
    cleaned["StockCode"] = cleaned["StockCode"].astype("string").str.strip()
    cleaned["Quantity"] = pd.to_numeric(cleaned["Quantity"], errors="coerce")
    cleaned["UnitPrice"] = pd.to_numeric(cleaned["UnitPrice"], errors="coerce")
    cleaned["InvoiceDate"] = pd.to_datetime(cleaned["InvoiceDate"], errors="coerce")

    invalid_date_rows = int(cleaned["InvoiceDate"].isna().sum())
    missing_required_rows = int(cleaned[required_columns].isna().any(axis=1).sum())
    cleaned = cleaned.dropna(subset=required_columns)

    cancelled_mask = cleaned["InvoiceNo"].str.upper().str.startswith("C", na=False)
    cancelled_rows = int(cancelled_mask.sum())
    cleaned = cleaned.loc[~cancelled_mask].copy()

    invalid_quantity_mask = cleaned["Quantity"] <= 0
    invalid_quantity_rows = int(invalid_quantity_mask.sum())
    cleaned = cleaned.loc[~invalid_quantity_mask].copy()

    invalid_price_mask = cleaned["UnitPrice"] <= 0
    invalid_price_rows = int(invalid_price_mask.sum())
    cleaned = cleaned.loc[~invalid_price_mask].copy()

    duplicate_rows = int(cleaned.duplicated().sum())
    cleaned = cleaned.drop_duplicates().copy()

    cleaned["Description"] = cleaned["Description"].astype("string").str.strip()
    missing_description_mask = cleaned["Description"].isna() | cleaned[
        "Description"
    ].eq("")
    missing_descriptions = int(missing_description_mask.sum())
    cleaned.loc[missing_description_mask, "Description"] = "Unknown product description"

    cleaned["Country"] = cleaned["Country"].astype("string").str.strip()
    missing_country_mask = cleaned["Country"].isna() | cleaned["Country"].eq("")
    missing_countries = int(missing_country_mask.sum())
    cleaned.loc[missing_country_mask, "Country"] = "Unknown country"

    # Customer IDs are not required to count sales. Keep these rows, but
    # exclude their missing IDs when calculating customer-level metrics.
    missing_customer_ids = int(cleaned["CustomerID"].isna().sum())

    cleaned["Revenue"] = cleaned["Quantity"] * cleaned["UnitPrice"]
    cleaned["Year"] = cleaned["InvoiceDate"].dt.year
    cleaned["Month"] = cleaned["InvoiceDate"].dt.month
    cleaned["Month_Name"] = cleaned["InvoiceDate"].dt.month_name()
    cleaned["Year_Month"] = cleaned["InvoiceDate"].dt.strftime("%Y-%m")
    cleaned = cleaned.reset_index(drop=True)

    cleaning_log = {
        "rows_before_cleaning": initial_rows,
        "rows_after_cleaning": len(cleaned),
        "missing_or_invalid_required_rows_removed": missing_required_rows,
        "invalid_dates_in_required_rows": invalid_date_rows,
        "cancelled_invoice_rows_removed": cancelled_rows,
        "non_positive_quantity_rows_removed": invalid_quantity_rows,
        "non_positive_unit_price_rows_removed": invalid_price_rows,
        "duplicate_rows_removed": duplicate_rows,
        "missing_descriptions_filled": missing_descriptions,
        "missing_countries_filled": missing_countries,
        "missing_customer_ids_kept": missing_customer_ids,
    }

    print("\nCleaning summary:")
    for decision, count in cleaning_log.items():
        print(f"  {decision.replace('_', ' ').capitalize()}: {count:,}")

    return cleaned, cleaning_log
