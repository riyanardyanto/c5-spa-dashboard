import pandas as pd
import httpx
import numpy as np
from typing import Optional, List
from pydantic import BaseModel, Field, ValidationError

from src.utils.auth import build_ntlm_auth
from src.utils.constants import HEADERS
from src.utils.app_config import AppDataConfig


def get_url_period_loss_tree(
    link_up: str, date: str, shift: str = "", functional_location: str = "PACK"
) -> str:
    from urllib.parse import urlencode
    from src.utils.app_config import get_base_url

    line_prefix = "PMID-SE-CP-L0" if link_up == "17" else "ID01-SE-CP-L0"
    params = {
        "table": "SPA_NormPeriodLossTree",
        "act": "query",
        "submit1": "Search",
        "db_Line": f"{line_prefix}{link_up}",
        "db_FunctionalLocation": f"{line_prefix}{link_up}-{functional_location}",
        "db_SegmentDateMin": date,
        "db_ShiftStart": shift,
        "db_SegmentDateMax": date,
        "db_ShiftEnd": shift,
        "db_Normalize": 0,
        "db_PeriodTime": 10080,
        "s_PeriodTime": "",
        "db_LongStopDetails": 3,
        "db_ReasonCNT": 30,
        "db_ReasonSort": "stop count",
        "db_Language": "OEM",
        "db_LineFailureAnalysis": "x",
    }

    base_url = get_base_url()
    return base_url + urlencode(params, doseq=True)


class LinePerformanceDetail(BaseModel):
    Line: str = Field(..., description="The line identifier")
    Detail: str = Field(..., description="Detailed description")
    Stops: Optional[str] = Field(None, description="Number of stops")
    Downtime: Optional[str] = Field(None, description="Downtime duration")


class DataLossesSummary(BaseModel):
    RANGE: str = Field(..., description="Time range")
    STOP: str = Field(..., description="Stop count")
    PR: str = Field(..., description="Performance rate")
    MTBF: str = Field(..., description="Mean time between failures")
    UPDT: str = Field(..., description="Unplanned downtime")
    PDT: str = Field(..., description="Planned downtime")
    NATR: str = Field(..., description="Natural rate loss")


class DataSPA(BaseModel):
    data_losses: DataLossesSummary
    stops_reason: List[LinePerformanceDetail]


class SPADataProcessor:
    """Processor for SPA data scraping, parsing, and validation."""

    def __init__(self, url: str, config: Optional[AppDataConfig] = None):
        self.url = url
        self.config = config
        self.list_of_dfs: list[pd.DataFrame] = []
        self.selected_table: pd.DataFrame = pd.DataFrame()
        self.spa_dict: dict[str, pd.DataFrame] = {}

    async def start(self) -> None:
        """Initialize the processor by fetching and processing data."""
        self.list_of_dfs = await self.fetch_and_process_spa_data(self.url)
        self.selected_table = self.select_relevant_table(self.list_of_dfs)
        self.spa_dict = self.split_table_into_dict()

    async def fetch_and_process_spa_data(self, url: str) -> list[pd.DataFrame]:
        """Fetch SPA data from URL and return list of DataFrames."""
        auth = build_ntlm_auth(self.config) if self.config else None
        try:
            async with httpx.AsyncClient(
                auth=auth, headers=HEADERS, timeout=30
            ) as client:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()
                from io import StringIO

                list_of_dfs = pd.read_html(StringIO(response.text), encoding="utf-8")
            return list_of_dfs
        except httpx.HTTPError as exc:
            status_code = (
                getattr(exc.response, "status_code", "unknown")
                if hasattr(exc, "response")
                else "unknown"
            )
            raise RuntimeError(
                f"Failed to fetch URL '{url}' (status code: {status_code}): {exc}. \n"
                "Check network connectivity, DNS resolution for the host, \n"
                "VPN/proxy settings, and the configured base URL in config.ini."
            ) from exc

    def select_relevant_table(self, list_of_dfs: list[pd.DataFrame]) -> pd.DataFrame:
        """Select the relevant table from list of DataFrames."""
        self.selected_table = next(
            (df for df in list_of_dfs if len(df) > 20), pd.DataFrame()
        )
        return self.selected_table

    def split_table_into_dict(self) -> dict[str, pd.DataFrame]:
        """Split the selected table into a dictionary of sections."""
        # Split the dataframe based on index of column 14 that contains "i"
        split_indices = np.where(self.selected_table.iloc[:, 14] == "i")[0].tolist()
        split_indices = [0] + split_indices + [len(self.selected_table)]
        sections = [
            self.selected_table.iloc[start:end].copy()
            for start, end in zip(split_indices, split_indices[1:])
        ]

        # Create a dictionary mapping keys to their corresponding dataframes
        spa_dict: dict[str, pd.DataFrame] = {}
        for section in sections:
            if len(section) < 2:
                continue
            key = str(section.iloc[0, 1]).replace(" ", "_").lower()
            spa_dict[key] = section.reset_index(drop=True)

        # Remove rows from spa_dict['time_range'] where column 2 and 3 values are 'nan'
        if "time_range" in spa_dict:
            spa_dict["time_range"] = spa_dict["time_range"].dropna(subset=[2, 3])

        return spa_dict

    async def get_line_performance_details(self) -> List[LinePerformanceDetail]:
        """Extract and validate line performance details."""
        try:
            # Process the "line_performance_details" dataframe
            line_performance_details = self.spa_dict.get(
                "line_performance_details", pd.DataFrame()
            )
            if line_performance_details.empty:
                return []

            line_performance_details = (
                line_performance_details[[1, 9, 2, 4]].iloc[1:].reset_index(drop=True)
            )

            # Normalize column 0: remove HTML non-breaking spaces and actual NBSP char,
            # strip whitespace (but don't remove letters like 'a'), treat empty/'nan' as missing,
            # forward-fill, then keep the left part before the first ' - ' if present.
            col = line_performance_details.iloc[:, 0]

            # Replace HTML entity and NBSP char, then strip surrounding whitespace
            col = (
                col.astype(str)
                .str.replace("&nbsp;", "", regex=False)
                .str.replace("&nbsp", "", regex=False)
                .str.strip()
            )

            # Convert empty strings and literal 'nan' (from astype) to missing values
            col = col.replace({"": pd.NA, "nan": pd.NA})

            # Forward-fill missing values then partition on ' - '
            col = col.ffill().str.partition(" - ")[0]

            line_performance_details.iloc[:, 0] = col

            # Remove rows where column 2 is NaN
            line_performance_details = line_performance_details.dropna(subset=[2])

            # Update column names
            line_performance_details.columns = [
                "Line",
                "Detail",
                "Stops",
                "Downtime",
            ]

            # Convert DataFrame to list of LinePerformanceDetail
            details = []
            for _, row in line_performance_details.iterrows():
                try:
                    detail = LinePerformanceDetail(
                        Line=str(row["Line"]),
                        Detail=str(row["Detail"]),
                        Stops=str(row["Stops"]) if pd.notna(row["Stops"]) else None,
                        Downtime=str(row["Downtime"])
                        if pd.notna(row["Downtime"])
                        else None,
                    )
                    details.append(detail)
                except ValidationError:
                    # Skip invalid rows
                    continue

            return details
        except Exception as e:
            raise ValueError(f"Failed to extract line performance details: {e}") from e

    async def get_data_losses_summary(self) -> DataLossesSummary:
        """Extract and validate data losses summary from the selected table."""
        try:
            data = {
                "RANGE": self.spa_dict["time_range"].iat[1, 9],
                "STOP": self.spa_dict["unplanned"].iat[1, 2],
                "PR": self.spa_dict["time_range"].iat[5, 5],
                "MTBF": self.spa_dict["time_range"].iat[5, 7],
                "UPDT": self.spa_dict["unplanned"].iat[1, 5],
                "PDT": self.spa_dict["planned"].iat[1, 5],
                "NATR": self.spa_dict["rate_loss"].iat[3, 5],
            }
            # Convert to strings and handle NaN
            cleaned_data = {k: ("" if pd.isna(v) else str(v)) for k, v in data.items()}
            return DataLossesSummary(**cleaned_data)
        except ValidationError as ve:
            raise ValueError(
                f"Pydantic validation error in data losses summary: {ve}"
            ) from ve
        except Exception as e:
            raise ValueError(f"Failed to extract data losses summary: {e}") from e

    async def get_data_spa(self) -> DataSPA:
        """Get the complete SPA data as a structured model."""
        data_losses = await self.get_data_losses_summary()
        stops_reason = await self.get_line_performance_details()
        return DataSPA(data_losses=data_losses, stops_reason=stops_reason)


def main():
    # Example usage
    url = "http://127.0.0.1:5501/assets/response.html"
    config = AppDataConfig(
        environment="development",
        username="user",
        password="pass",
        link_up=("LU18", "LU21"),
        url=url,
        verify_ssl=True,
    )

    import asyncio

    async def run():
        from tabulate import tabulate

        processor = SPADataProcessor(url, config)
        await processor.start()
        data_spa = await processor.get_data_spa()

        with open("x1 data_losses.txt", "w", encoding="utf-8") as f:
            f.write("Data Losses Summary:\n")
            f.write(
                tabulate(
                    [data_spa.data_losses.model_dump().values()],
                    headers=data_spa.data_losses.model_dump().keys(),
                    tablefmt="psql",
                )
            )
            f.write("\n\n")

        with open("x2 line_performance_details.txt", "w", encoding="utf-8") as f:
            f.write("Line Performance Details:\n")
            # Convert list of models to list of dicts for tabulate
            details_data = [detail.model_dump() for detail in data_spa.stops_reason]
            if details_data:
                f.write(tabulate(details_data, headers="keys", tablefmt="psql"))
            else:
                f.write("No data available.\n")
            f.write("\n\n")

        # print("Data Losses Summary:")
        # print(data_losses)

    asyncio.run(run())


if __name__ == "__main__":
    main()


# # Legacy functions for backward compatibility (can be removed if not needed)
# async def fetch_and_process_spa_data(url: str, config: Optional[AppDataConfig] = None):
#     processor = SPADataProcessor(url, config)
#     await processor.initialize()
#     return processor.list_of_dfs


# def select_relevant_table(list_of_dfs: list[pd.DataFrame]) -> pd.DataFrame:
#     processor = SPADataProcessor("", None)
#     return processor.select_relevant_table(list_of_dfs)


# def split_table_into_dict(selected_table: pd.DataFrame) -> dict[str, pd.DataFrame]:
#     processor = SPADataProcessor("", None)
#     return processor.split_table_into_dict(selected_table)


# async def get_line_performance_details() -> pd.DataFrame:
#     # This would need a processor instance, but for legacy, perhaps not
#     pass


# async def get_data_losses_summary() -> DataLossesSummary:
#     # This would need a processor instance
#     pass
