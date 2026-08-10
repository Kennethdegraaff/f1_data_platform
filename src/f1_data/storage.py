from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq


def write_parquet(records: list[dict], output_path: Path) -> None:
    table = pa.Table.from_pylist(records)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    pq.write_table(table, output_path)