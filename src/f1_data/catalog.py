import boto3
from botocore.exceptions import ClientError


def add_results_partition(
    season: int,
    round_number: int,
    bucket: str,
) -> None:
    glue = boto3.client("glue")

    try:
        glue.batch_create_partition(
            DatabaseName="f1_data",
            TableName="results",
            PartitionInputList=[
                {
                    "Values": [str(round_number)],
                    "StorageDescriptor": {
                        "Location": (
                            f"s3://{bucket}/"
                            f"data_collected/{season}/"
                            f"results/round={round_number}/"
                        ),
                    },
                }
            ],
        )

        print(f"  ✓ Registered Glue partition for round {round_number}")

    except ClientError as exc:
        error_code = exc.response["Error"]["Code"]

        if error_code == "AlreadyExistsException":
            print(
                f"  ○ Glue partition for round {round_number} already exists"
            )
            return

        raise