"""Load and inspect the source Excel workbook."""

from pathlib import Path
import zipfile

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_PATH = PROJECT_ROOT / "data" / "Online Retail.xlsx"
DATASET_DOWNLOAD_PAGE = "https://archive.ics.uci.edu/dataset/352/online+retail"


def load_data(file_path: str | Path = DEFAULT_DATASET_PATH) -> pd.DataFrame:
    """Load the original workbook without modifying it."""
    dataset_path = Path(file_path)
    if not dataset_path.is_absolute():
        dataset_path = PROJECT_ROOT / dataset_path

    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {dataset_path}\n"
            "Download Online Retail.xlsx from the UCI Machine Learning Repository:\n"
            f"{DATASET_DOWNLOAD_PAGE}\n"
            f"Save the workbook as {DEFAULT_DATASET_PATH.name} in {DEFAULT_DATASET_PATH.parent}."
        )

    try:
        from openpyxl.utils.exceptions import InvalidFileException

        data = pd.read_excel(dataset_path, engine="openpyxl")
    except ImportError as error:
        raise ImportError(
            "Excel support is unavailable. Install the project dependencies with "
            "`python -m pip install -r requirements.txt`."
        ) from error
    except (OSError, ValueError, zipfile.BadZipFile, InvalidFileException) as error:
        raise RuntimeError(
            f"Could not read the Excel workbook at {dataset_path}. "
            "Check that the file is a valid, readable .xlsx workbook."
        ) from error

    if data.empty:
        raise ValueError(f"The workbook contains no transaction rows: {dataset_path}")

    return data


def inspect_data(data: pd.DataFrame) -> None:
    """Print a concise overview of the loaded data before cleaning."""
    print("\nFirst five rows:")
    print(data.head())
    print(f"\nDataset dimensions: {data.shape[0]:,} rows x {data.shape[1]} columns")
    print("\nColumn names and data types:")
    print(data.dtypes.to_string())
    print("\nMissing values by column:")
    print(data.isna().sum().to_string())
