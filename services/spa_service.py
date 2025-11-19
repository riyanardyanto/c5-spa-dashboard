from __future__ import annotations

from io import StringIO
from typing import TYPE_CHECKING
from urllib.parse import urlencode

import numpy as np
import pandas as pd
import requests
from requests import Session
from tabulate import tabulate

from utils.auth import build_ntlm_auth
from utils.constants import HEADERS
from utils.app_config import get_base_url

if TYPE_CHECKING:
    from utils.app_config import AppDataConfig


def get_url_period_loss_tree(
    link_up: str, date: str, shift: str = "", functional_location: str = "PACK"
) -> str:
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

    """http://ots.app.pmi/db.aspx?table=SPA_NormPeriodLossTree&act=query&submit1=Search&db_Line=ID01-SE-CP-L021&db_FunctionalLocation=ID01-SE-CP-L021-MAKE&db_SegmentDateMin=2025-11-08&db_ShiftStart=&db_SegmentDateMax=&db_ShiftEnd=&db_Normalize=0&db_PeriodTime=10080&s_PeriodTime=&db_LongStopDetails=3&db_ReasonCNT=30&db_ReasonSort=stop+count&db_Language=OEM&db_LineFailureAnalysis=x"""

    # Read base URL from config.ini using centralized helper
    base_url = get_base_url()

    return base_url + urlencode(params, doseq=True)


class SPADataFetcher:
    """Handles fetching data from URLs."""

    def __init__(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        auth=None,
        config: AppDataConfig | None = None,
        session: Session | None = None,
    ) -> None:
        self.url = url
        self.raw_html: str | None = None
        self._headers = headers or HEADERS
        self._auth = auth if auth is not None else build_ntlm_auth(config)
        self._session = session
        self._config = config

    def fetch(self, session: Session | None = None) -> str:
        """Fetch HTML content from the URL synchronously."""

        if self.raw_html is not None:
            return self.raw_html

        active_session = session or self._session

        if active_session is not None:
            try:
                response = active_session.get(
                    self.url,
                    headers=self._headers,
                    auth=self._auth,
                    allow_redirects=True,
                    timeout=30,
                )
                response.raise_for_status()
                text = response.text
            except requests.exceptions.RequestException as exc:
                # Provide a clearer, actionable error message for name resolution
                raise RuntimeError(
                    f"Failed to fetch URL '{self.url}': {exc}. "
                    "Check network connectivity, DNS resolution for the host, "
                    "VPN/proxy settings, and the configured base URL in config.ini."
                ) from exc
        else:
            with requests.Session() as temp_session:
                try:
                    response = temp_session.get(
                        self.url,
                        headers=self._headers,
                        auth=self._auth,
                        allow_redirects=True,
                        timeout=30,
                    )
                    response.raise_for_status()
                    text = response.text
                except requests.exceptions.RequestException as exc:
                    raise RuntimeError(
                        f"Failed to fetch URL '{self.url}': {exc}. "
                        "Check network connectivity, DNS resolution for the host, "
                        "VPN/proxy settings, and the configured base URL in config.ini."
                    ) from exc

        self.raw_html = text
        return self.raw_html


class HTMLTableExtractor:
    """Extracts and processes tables from HTML content."""

    def __init__(self, html_content: str):
        self.html_content = html_content
        self.tables: list[pd.DataFrame] = []

    def extract(self) -> list[pd.DataFrame]:
        """Extract tables from HTML and replace empty strings with NaN."""
        tables = pd.read_html(StringIO(self.html_content))
        if not tables:
            raise ValueError("No tables found in the HTML content.")

        # Replace empty strings and &nbsp-like values with np.nan in all tables
        self.tables = [
            table.replace({"": np.nan}).replace(
                to_replace=r".*&nbsp.*", value=np.nan, regex=True
            )
            for table in tables
        ]
        return self.tables


class DataFrameCleaner:
    """Handles DataFrame cleaning operations."""

    @staticmethod
    def remove_duplicate_rows(df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove rows where column '1' has the same value as the previous row
        AND column '2' is NaN.
        """
        # Remove row that all columns are NaN
        df = df.dropna(how="all").reset_index(drop=True)

        if df.empty:
            return df

        mask = ~((df[1] == df[1].shift()) & df[2].isna())
        mask.iloc[0] = True
        return df[mask].reset_index(drop=True)


class DataFrameSplitter:
    """Splits DataFrames based on specific column values."""

    def __init__(self, tables: list[pd.DataFrame]):
        self.tables = tables
        self.sections: list[pd.DataFrame] = []

    def split_by_column_14(self) -> list[pd.DataFrame]:
        """Split the fourth table by rows where column 14 has value 'i'."""
        # Select the table with more than 20 rows
        for table in self.tables:
            if len(table) > 20:
                datatable = table
                break

        # Remove duplicate rows
        datatable = DataFrameCleaner.remove_duplicate_rows(datatable)

        # Find indices where column 14 has value "i"
        split_indices = np.flatnonzero(datatable[14] == "i")

        if split_indices.size == 0:
            self.sections = [datatable.copy()]
            return self.sections

        bounds = np.append(split_indices[1:], len(datatable))
        self.sections = [
            datatable.iloc[start:end].copy()
            for start, end in zip(split_indices, bounds)
        ]

        return self.sections


class StopReasonTableProcessor:
    """Processes stop reason table from splitted tables."""

    def __init__(self, splitted_tables: list[pd.DataFrame]):
        self.splitted_tables = splitted_tables

    def process(self) -> pd.DataFrame:
        """Get and process the stops reason table from splitted tables."""
        table = self.splitted_tables[3]
        cleaned = table.dropna(how="all")
        stops_reason = (
            cleaned.loc[cleaned[4].notna(), [1, 9, 2, 4]]
            .iloc[1:]
            .reset_index(drop=True)
        )

        stops_reason.columns = ["Line", "Reason", "Stops", "Downtime"]
        stops_reason["Line"] = stops_reason["Line"].ffill().str.partition(" - ")[0]

        return stops_reason


class DataLossesTableProcessor:
    """Processes data losses table from splitted tables."""

    def __init__(self, splitted_tables: list[pd.DataFrame]):
        self.splitted_tables = splitted_tables

    def process(self) -> pd.DataFrame:
        """Extract and combine data losses metrics from splitted tables."""
        tables = self.splitted_tables
        data = {
            "RANGE": tables[0].iat[1, 9],
            "STOP": tables[7].iat[1, 2],
            "PR": tables[0].iat[5, 5],
            "MTBF": tables[0].iat[5, 7],
            "UPDT": tables[7].iat[1, 5],
            "PDT": tables[6].iat[1, 5],
            "NATR": tables[4].iat[3, 5],
        }

        return pd.DataFrame([data])


class SPADataProcessor:
    """Main processor that orchestrates all data processing operations."""

    def __init__(
        self,
        url: str,
        *,
        is_html: bool = False,
        headers: dict[str, str] | None = None,
        auth=None,
        config: AppDataConfig | None = None,
        session: Session | None = None,
    ) -> None:
        self._source = url
        self._is_html = is_html
        self._headers = headers or HEADERS
        self._config = config
        self._auth = auth if auth is not None else build_ntlm_auth(config)
        self._session = session
        self.fetcher: SPADataFetcher | None = None
        self.raw_html: str | None = url if is_html else None
        self.tables: list[pd.DataFrame] = []
        self.splitted_tables: list[pd.DataFrame] = []
        self.processed_data: dict[str, pd.DataFrame] = {}

        if not is_html:
            self.fetcher = SPADataFetcher(
                url,
                headers=self._headers,
                auth=self._auth,
                config=self._config,
                session=session,
            )

    def process(
        self,
        *,
        session: Session | None = None,
        force: bool = False,
    ) -> dict[str, pd.DataFrame]:
        """Execute the full data processing pipeline synchronously."""

        if self.processed_data and not force:
            return self.processed_data

        if self.raw_html is None:
            if self.fetcher is None:
                self.fetcher = SPADataFetcher(
                    self._source,
                    headers=self._headers,
                    auth=self._auth,
                    config=self._config,
                    session=self._session,
                )
            self.raw_html = self.fetcher.fetch(session=session)

        extractor = HTMLTableExtractor(self.raw_html)
        self.tables = extractor.extract()

        splitter = DataFrameSplitter(self.tables)
        self.splitted_tables = splitter.split_by_column_14()

        self.processed_data = {
            "data_losses": DataLossesTableProcessor(self.splitted_tables).process(),
            "stops_reason": StopReasonTableProcessor(self.splitted_tables).process(),
        }

        return self.processed_data

    def save_results(self, output_format: str = "psql") -> None:
        """Save processed data to files after ensuring processing."""

        self.process()

        for key, df in self.processed_data.items():
            filename = f"{key}.txt"
            with open(filename, "w", encoding="utf-8") as file_handle:
                file_handle.write(
                    tabulate(
                        df,
                        headers="keys",
                        tablefmt=output_format,
                        showindex=False,
                    )
                )

    def display_results(self) -> None:
        """Display processed data to console."""

        if not self.processed_data:
            raise RuntimeError(
                "Data belum diproses. Panggil 'process()' sebelum tampilkan hasil."
            )

        for key, df in self.processed_data.items():
            print(f"\n=== {key.upper()} ===")
            print(tabulate(df, headers="keys", tablefmt="psql", showindex=False))


def main() -> None:
    processor = SPADataProcessor("http://127.0.0.1:5501/assets/spa1.html")
    processor.process()
    processor.display_results()
    processor.save_results()


if __name__ == "__main__":
    main()
