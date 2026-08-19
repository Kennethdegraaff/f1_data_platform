from pathlib import Path

import boto3
import pyarrow as pa
import pyarrow.parquet as pq


def parquet_exists(
    output_path: Path,
    bucket: str | None = None,
) -> bool:
    print(f"parquet_exists: bucket={bucket!r}, key={str(output_path)!r}")

    if bucket is None:
        exists = output_path.exists()
        print(f"parquet_exists: local exists={exists}")
        return exists

    s3 = boto3.client("s3")

    try:
        s3.head_object(
            Bucket=bucket,
            Key=str(output_path),
        )
        print("parquet_exists: S3 object EXISTS")
        return True
    except s3.exceptions.ClientError as exc:
        error_code = exc.response["Error"]["Code"]
        print(f"parquet_exists: S3 error={error_code!r}")

        if error_code in ("404", "NoSuchKey", "NotFound"):
            return False

        raise

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