from pathlib import Path

import boto3
import pyarrow as pa
import pyarrow.parquet as pq
from botocore.exceptions import ClientError


def parquet_exists(
    output_path: Path,
    bucket: str,
) -> bool:
    print(f"parquet_exists: bucket={bucket!r}, key={str(output_path)!r}")

    s3 = boto3.client("s3")

    try:
        s3.head_object(
            Bucket=bucket,
            Key=str(output_path),
        )
        print("parquet_exists: S3 object EXISTS")
        return True

    except ClientError as exc:
        error_code = exc.response["Error"]["Code"]

        if error_code in ("404", "NoSuchKey", "NotFound"):
            print("parquet_exists: S3 object does not exist yet")
            return False

        print(f"parquet_exists: S3 error={error_code!r}")
        raise


def write_parquet(
    records: list[dict],
    output_path: Path,
    bucket: str,
) -> None:
    table = pa.Table.from_pylist(records)

    s3 = boto3.client("s3")

    buffer = pa.BufferOutputStream()
    pq.write_table(table, buffer)

    s3.put_object(
        Bucket=bucket,
        Key=str(output_path),
        Body=buffer.getvalue().to_pybytes(),
    )