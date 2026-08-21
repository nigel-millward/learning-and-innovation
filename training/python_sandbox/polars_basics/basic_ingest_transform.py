import os
import logging

import polars as pl
from polars.exceptions import ComputeError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def ingest(input_file_path: str) -> pl.LazyFrame:
    """Lazily scan the CSV so the transform can be query-optimised."""
    try:
        lf = pl.scan_csv(input_file_path, has_header=True, separator=",")
        # trigger schema resolution so we fail fast on a missing/bad file
        lf.collect_schema()
        return lf
    except FileNotFoundError:
        logger.error(f"File not found: {input_file_path}")
        raise
    except ComputeError as e:
        logger.error(f"File format error: the file is corrupt or not a valid CSV. Details: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise


def transform(lf: pl.LazyFrame) -> pl.LazyFrame:
    lf_cleaned = lf.drop("diet")
    logger.info("diet has been dropped")
    return lf_cleaned


def main():
    script_dir = os.path.dirname(__file__)
    input_file_path = os.path.join(script_dir, "input.csv")
    output_file_path = os.path.join(script_dir, "output.csv")

    lf = ingest(input_file_path)
    lf_cleaned = transform(lf)

    lf_cleaned.sink_csv(output_file_path)
    logger.info(f"write successful: {output_file_path}")


if __name__ == "__main__":
    main()
