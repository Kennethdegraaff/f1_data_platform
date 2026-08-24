from pathlib import Path
from unittest.mock import patch

from f1_data.storage import parquet_exists, write_parquet


@patch("f1_data.storage.boto3.client")
def test_write_parquet_to_s3(mock_boto_client) -> None:
    mock_s3 = mock_boto_client.return_value

    records = [
        {"driver_id": "russell", "points": 25},
    ]

    write_parquet(
        records,
        Path("processed/2026/test.parquet"),
        bucket="f1-data-platform",
    )

    mock_boto_client.assert_called_once_with("s3")

    mock_s3.put_object.assert_called_once()

    call_kwargs = mock_s3.put_object.call_args.kwargs

    assert call_kwargs["Bucket"] == "f1-data-platform"
    assert call_kwargs["Key"] == "processed/2026/test.parquet"


@patch("f1_data.storage.boto3.client")
def test_parquet_exists_in_s3(mock_boto_client) -> None:
    mock_s3 = mock_boto_client.return_value

    exists = parquet_exists(
        Path("processed/2026/results.parquet"),
        bucket="f1-data-platform",
    )

    assert exists is True

    mock_s3.head_object.assert_called_once_with(
        Bucket="f1-data-platform",
        Key="processed/2026/results.parquet",
    )


@patch("f1_data.storage.boto3.client")
def test_parquet_does_not_exist_in_s3(mock_boto_client) -> None:
    mock_s3 = mock_boto_client.return_value

    error = {
        "Error": {
            "Code": "404",
        }
    }

    from botocore.exceptions import ClientError

    mock_s3.head_object.side_effect = ClientError(
        error,
        "HeadObject",
    )

    exists = parquet_exists(
        Path("processed/2026/results.parquet"),
        bucket="f1-data-platform",
    )

    assert exists is False