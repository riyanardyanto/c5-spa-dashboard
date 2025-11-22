import asyncio
import pandas as pd

from src.services.spa_service import SPADataProcessor


def test_line_performance_cleaning_and_partition():
    # Create a DataFrame matching the shape expected by the processor
    # The processor selects columns [1, 9, 2, 4] and drops the first row (.iloc[1:])
    rows = [
        # header row (to be removed by .iloc[1:])
        [None] * 10,
        # real rows: (cols 1,9,2,4 are the interesting ones)
        [None, "Line A", 3, None, "00:05", None, None, None, None, "Detail A"],
        [None, "&nbsp;", 1, None, "00:06", None, None, None, None, "Detail B"],
        [
            None,
            "\u00a0SubLine - extra",
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            "Detail C",
        ],
        [None, "Line B - extra", 2, None, "00:12", None, None, None, None, "Detail D"],
    ]

    df = pd.DataFrame(rows, columns=list(range(10)))

    processor = SPADataProcessor(url="", config=None)
    # Put our crafted DataFrame into spa_dict where get_line_performance_details expects it
    processor.spa_dict = {"line_performance_details": df}

    # Call the async method
    details = asyncio.run(processor.get_line_performance_details())

    # After cleaning, we should have 3 rows (one is dropped because col 2 was NaN in that row)
    assert isinstance(details, list)
    assert len(details) == 3

    # Check the cleaned 'Line' values and that partitioning worked
    assert details[0].Line == "Line A"
    # second row was &nbsp; and should have been forward-filled with previous 'Line A'
    assert details[1].Line == "Line A"
    # fourth row contained '\u00A0SubLine - extra' but had missing Stops and should be dropped; next is Line B
    assert details[2].Line == "Line B"
