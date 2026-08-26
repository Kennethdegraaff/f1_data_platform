from unittest.mock import Mock, patch

import pytest
from botocore.exceptions import ClientError

from f1_data.catalog import (
    add_constructor_standings_partition,
    add_driver_standings_partition,
    add_results_partition,
    add_sprint_partition,
)


def test_add_results_partition() -> None:
    glue = Mock()

    with patch("f1_data.catalog.boto3.client", return_value=glue):
        add_results_partition(
            season=2026,
            round_number=12,
            bucket="f1-data-platform",
        )

    glue.batch_create_partition.assert_called_once_with(
        DatabaseName="f1_data",
        TableName="results",
        PartitionInputList=[
            {
                "Values": ["12"],
                "StorageDescriptor": {
                    "Location": (
                        "s3://f1-data-platform/"
                        "data_collected/2026/"
                        "results/round=12/"
                    ),
                },
            }
        ],
    )


def test_existing_partition_is_ignored() -> None:
    glue = Mock()

    error = ClientError(
        {
            "Error": {
                "Code": "AlreadyExistsException",
                "Message": "Partition already exists",
            }
        },
        "BatchCreatePartition",
    )

    glue.batch_create_partition.side_effect = error

    with patch("f1_data.catalog.boto3.client", return_value=glue):
        add_results_partition(
            season=2026,
            round_number=12,
            bucket="f1-data-platform",
        )


def test_unexpected_glue_error_is_raised() -> None:
    glue = Mock()

    error = ClientError(
        {
            "Error": {
                "Code": "AccessDeniedException",
                "Message": "Access denied",
            }
        },
        "BatchCreatePartition",
    )

    glue.batch_create_partition.side_effect = error

    with (
        patch("f1_data.catalog.boto3.client", return_value=glue),
        pytest.raises(ClientError),
    ):
        add_results_partition(
            season=2026,
            round_number=12,
            bucket="f1-data-platform",
        )


def test_new_dataset_partitions_use_expected_values_and_locations() -> None:
    glue = Mock()

    with patch("f1_data.catalog.boto3.client", return_value=glue):
        add_sprint_partition(2026, 2, "f1-data-platform")
        add_driver_standings_partition(2026, 12, "f1-data-platform")
        add_constructor_standings_partition(2026, 12, "f1-data-platform")

    calls = glue.batch_create_partition.call_args_list

    assert calls[0].kwargs["TableName"] == "sprint"
    assert calls[0].kwargs["PartitionInputList"][0]["Values"] == ["2"]
    assert calls[1].kwargs["TableName"] == "driver_standings"
    assert calls[1].kwargs["PartitionInputList"][0]["Values"] == ["2026", "12"]
    assert calls[1].kwargs["PartitionInputList"][0]["StorageDescriptor"][
        "Location"
    ] == (
        "s3://f1-data-platform/data_collected/driver_standings/"
        "season=2026/round=12/"
    )
    assert calls[2].kwargs["TableName"] == "constructor_standings"
