from unittest.mock import Mock, patch

import pytest
from botocore.exceptions import ClientError

from f1_data.catalog import add_results_partition


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