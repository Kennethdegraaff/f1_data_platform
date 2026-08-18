from pathlib import Path
from unittest.mock import patch

from f1_data.storage import parquet_exists, write_parquet


def test_write_parquet(tmp_path: Path) -> None:
    output_path = tmp_path / "data" / "test.parquet"

    records = [
        {"driver_id": "russell", "points": 25},
        {"driver_id": "leclerc", "points": 18},
    ]

    write_parquet(records, output_path)

    assert output_path.exists()

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

def test_parquet_exists_locally(tmp_path: Path) -> None:
    output_path = tmp_path / "test.parquet"

    assert not parquet_exists(output_path)

    output_path.touch()

    assert parquet_exists(output_path)

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