from datetime import date

import pandas as pd


WORKFORCE_SOURCES = {
    "Federal Public Service": "Federal Public Service",
    "RCMP": "RCMP",
    "CAF": "CAF",
}


def convert_period(value):
    """
    Convert a YYYYMM source value to the first day of that month.
    """
    value = int(value)

    year = value // 100
    month = value % 100

    return date(year, month, 1)


def prepare_workforce_records(workbook):
    """
    Combine all workforce sheets into one database-ready DataFrame.

    Preserve the source of every record.
    """
    frames = []

    for sheet_name, source_name in WORKFORCE_SOURCES.items():
        dataframe = workbook[sheet_name].copy()

        dataframe["source"] = source_name

        if "fte" not in dataframe.columns:
            dataframe["fte"] = pd.NA

        dataframe["period"] = dataframe["date"].map(convert_period)

        dataframe = dataframe[
            [
                "period",
                "source",
                "department",
                "tenure",
                "headcount",
                "fte",
            ]
        ]

        frames.append(dataframe)

    return pd.concat(frames, ignore_index=True)