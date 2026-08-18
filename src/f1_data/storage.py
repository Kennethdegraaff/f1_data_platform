from pathlib import Path

import boto3
import pyarrow as pa
import pyarrow.parquet as pq


def parquet_exists(
    output_path: Path,
    bucket: str | None = None,
) -> bool:
    if bucket is None:
        return output_path.exists()

    s3 = boto3.client("s3")

    try:
        s3.head_object(
            Bucket=bucket,
            Key=str(output_path),
        )
    except s3.exceptions.ClientError as exc:
        if exc.response["Error"]["Code"] == "404":
            return False
        raise

    return True

def write_parquet(
    records: list[dict],
    output_path: Path,
    bucket: str | None = None,
) -> None:
    table = pa.Table.from_pylist(records)

    if bucket is None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        pq.write_table(table, output_path)
        return

    s3 = boto3.client("s3")

    buffer = pa.BufferOutputStream()
    pq.write_table(table, buffer)

    s3.put_object(
        Bucket=bucket,
        Key=str(output_path),
        Body=buffer.getvalue().to_pybytes(),
    )