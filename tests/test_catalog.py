from unittest.mock import Mock, patch

from botocore.exceptions import ClientError

from f1_data.catalog import (
    add_constructor_standings_partition,
    add_driver_standings_partition,
    add_reference_partition,
    add_results_partition,
    add_sprint_partition,
)


BUCKET = "f1-data-platform"
DATABASE_NAME = "f1_data"


def storage_descriptor() -> dict:
    return {
        "Columns": [],
        "InputFormat": (
            "org.apache.hadoop.hive.ql.io.parquet."
            "MapredParquetInputFormat"
        ),
        "OutputFormat": (
            "org.apache.hadoop.hive.ql.io.parquet."
            "MapredParquetOutputFormat"
        ),
        "SerdeInfo": {
            "SerializationLibrary": (
                "org.apache.hadoop.hive.ql.io.parquet.serde."
                "ParquetHiveSerDe"
            ),
            "Parameters": {},
        },
        "Compressed": False,
        "NumberOfBuckets": 0,
        "SortColumns": [],
        "StoredAsSubDirectories": False,
    }


def configure_glue_table(glue: Mock) -> None:
    glue.get_table.return_value = {
        "Table": {
            "StorageDescriptor": storage_descriptor(),
        }
    }


def expected_storage_descriptor(location: str) -> dict:
    descriptor = storage_descriptor()
    descriptor["Location"] = location

    return descriptor


def test_add_results_partition() -> None:
    glue = Mock()
    configure_glue_table(glue)

    with patch("f1_data.catalog.boto3.client", return_value=glue):
        add_results_partition(
            season=2026,
            round_number=12,
            bucket=BUCKET,
            database_name=DATABASE_NAME,
        )

    glue.get_table.assert_called_once_with(
        DatabaseName=DATABASE_NAME,
        Name="race_results",
    )

    glue.batch_create_partition.assert_called_once_with(
        DatabaseName=DATABASE_NAME,
        TableName="race_results",
        PartitionInputList=[
            {
                "Values": ["2026", "12"],
                "StorageDescriptor": expected_storage_descriptor(
                    f"s3://{BUCKET}/"
                    "data_collected/race_results/"
                    "season=2026/round=12/"
                ),
            }
        ],
    )


def test_add_sprint_partition() -> None:
    glue = Mock()
    configure_glue_table(glue)

    with patch("f1_data.catalog.boto3.client", return_value=glue):
        add_sprint_partition(
            season=2026,
            round_number=2,
            bucket=BUCKET,
            database_name=DATABASE_NAME,
        )

    glue.get_table.assert_called_once_with(
        DatabaseName=DATABASE_NAME,
        Name="sprint_results",
    )

    glue.batch_create_partition.assert_called_once_with(
        DatabaseName=DATABASE_NAME,
        TableName="sprint_results",
        PartitionInputList=[
            {
                "Values": ["2026", "2"],
                "StorageDescriptor": expected_storage_descriptor(
                    f"s3://{BUCKET}/"
                    "data_collected/sprint_results/"
                    "season=2026/round=2/"
                ),
            }
        ],
    )


def test_add_driver_standings_partition() -> None:
    glue = Mock()
    configure_glue_table(glue)

    with patch("f1_data.catalog.boto3.client", return_value=glue):
        add_driver_standings_partition(
            season=2026,
            round_number=12,
            bucket=BUCKET,
            database_name=DATABASE_NAME,
        )

    glue.get_table.assert_called_once_with(
        DatabaseName=DATABASE_NAME,
        Name="driver_standings",
    )

    glue.batch_create_partition.assert_called_once_with(
        DatabaseName=DATABASE_NAME,
        TableName="driver_standings",
        PartitionInputList=[
            {
                "Values": ["2026", "12"],
                "StorageDescriptor": expected_storage_descriptor(
                    f"s3://{BUCKET}/"
                    "data_collected/driver_standings/"
                    "season=2026/round=12/"
                ),
            }
        ],
    )


def test_add_constructor_standings_partition() -> None:
    glue = Mock()
    configure_glue_table(glue)

    with patch("f1_data.catalog.boto3.client", return_value=glue):
        add_constructor_standings_partition(
            season=2026,
            round_number=12,
            bucket=BUCKET,
            database_name=DATABASE_NAME,
        )

    glue.get_table.assert_called_once_with(
        DatabaseName=DATABASE_NAME,
        Name="constructor_standings",
    )

    glue.batch_create_partition.assert_called_once_with(
        DatabaseName=DATABASE_NAME,
        TableName="constructor_standings",
        PartitionInputList=[
            {
                "Values": ["2026", "12"],
                "StorageDescriptor": expected_storage_descriptor(
                    f"s3://{BUCKET}/"
                    "data_collected/constructor_standings/"
                    "season=2026/round=12/"
                ),
            }
        ],
    )


def test_add_reference_partition() -> None:
    glue = Mock()
    configure_glue_table(glue)

    with patch("f1_data.catalog.boto3.client", return_value=glue):
        add_reference_partition(
            dataset="races",
            season=2026,
            bucket=BUCKET,
            database_name=DATABASE_NAME,
        )

    glue.get_table.assert_called_once_with(
        DatabaseName=DATABASE_NAME,
        Name="races",
    )

    glue.batch_create_partition.assert_called_once_with(
        DatabaseName=DATABASE_NAME,
        TableName="races",
        PartitionInputList=[
            {
                "Values": ["2026"],
                "StorageDescriptor": expected_storage_descriptor(
                    f"s3://{BUCKET}/"
                    "data_collected/races/"
                    "season=2026/"
                ),
            }
        ],
    )


def test_add_reference_partition_for_drivers() -> None:
    glue = Mock()
    configure_glue_table(glue)

    with patch("f1_data.catalog.boto3.client", return_value=glue):
        add_reference_partition(
            dataset="drivers",
            season=2026,
            bucket=BUCKET,
            database_name=DATABASE_NAME,
        )

    glue.get_table.assert_called_once_with(
        DatabaseName=DATABASE_NAME,
        Name="drivers",
    )

    glue.batch_create_partition.assert_called_once_with(
        DatabaseName=DATABASE_NAME,
        TableName="drivers",
        PartitionInputList=[
            {
                "Values": ["2026"],
                "StorageDescriptor": expected_storage_descriptor(
                    f"s3://{BUCKET}/"
                    "data_collected/drivers/"
                    "season=2026/"
                ),
            }
        ],
    )


def test_add_reference_partition_for_constructors() -> None:
    glue = Mock()
    configure_glue_table(glue)

    with patch("f1_data.catalog.boto3.client", return_value=glue):
        add_reference_partition(
            dataset="constructors",
            season=2026,
            bucket=BUCKET,
            database_name=DATABASE_NAME,
        )

    glue.get_table.assert_called_once_with(
        DatabaseName=DATABASE_NAME,
        Name="constructors",
    )

    glue.batch_create_partition.assert_called_once_with(
        DatabaseName=DATABASE_NAME,
        TableName="constructors",
        PartitionInputList=[
            {
                "Values": ["2026"],
                "StorageDescriptor": expected_storage_descriptor(
                    f"s3://{BUCKET}/"
                    "data_collected/constructors/"
                    "season=2026/"
                ),
            }
        ],
    )


def test_add_partition_ignores_already_existing_partition() -> None:
    glue = Mock()
    configure_glue_table(glue)

    error = {
        "Error": {
            "Code": "AlreadyExistsException",
        }
    }

    glue.batch_create_partition.side_effect = ClientError(
        error,
        "BatchCreatePartition",
    )

    with patch("f1_data.catalog.boto3.client", return_value=glue):
        add_results_partition(
            season=2026,
            round_number=12,
            bucket=BUCKET,
            database_name=DATABASE_NAME,
        )

    glue.batch_create_partition.assert_called_once()


def test_add_partition_reraises_unexpected_client_error() -> None:
    glue = Mock()
    configure_glue_table(glue)

    error = {
        "Error": {
            "Code": "InternalServiceException",
        }
    }

    glue.batch_create_partition.side_effect = ClientError(
        error,
        "BatchCreatePartition",
    )

    with patch("f1_data.catalog.boto3.client", return_value=glue):
        try:
            add_results_partition(
                season=2026,
                round_number=12,
                bucket=BUCKET,
                database_name=DATABASE_NAME,
            )
        except ClientError:
            pass
        else:
            raise AssertionError(
                "Expected ClientError to be re-raised"
            )