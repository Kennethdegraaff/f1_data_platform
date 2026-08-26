import boto3

from botocore.exceptions import ClientError


def add_partition(
    table_name: str,
    partition_values: list[str],
    location: str,
    database_name: str,
) -> None:
    glue = boto3.client("glue")

    try:
        glue.batch_create_partition(
            DatabaseName=database_name,
            TableName=table_name,
            PartitionInputList=[
                {
                    "Values": partition_values,
                    "StorageDescriptor": {
                        "Location": location,
                    },
                }
            ],
        )

        print(f"  ✓ Registered Glue partition for {table_name}")

    except ClientError as exc:
        error_code = exc.response["Error"]["Code"]

        if error_code == "AlreadyExistsException":
            print(f"  ○ Glue partition for {table_name} already exists")
            return

        raise


def add_results_partition(
    season: int,
    round_number: int,
    bucket: str,
    database_name: str,
) -> None:
    add_partition(
        table_name="race_results",
        partition_values=[str(season), str(round_number)],
        location=(
            f"s3://{bucket}/data_collected/race_results/"
            f"season={season}/round={round_number}/"
        ),
        database_name=database_name,
    )


def add_sprint_partition(
    season: int,
    round_number: int,
    bucket: str,
    database_name: str,
) -> None:
    add_partition(
        table_name="sprint_results",
        partition_values=[str(season), str(round_number)],
        location=(
            f"s3://{bucket}/data_collected/sprint_results/"
            f"season={season}/round={round_number}/"
        ),
        database_name=database_name,
    )


def add_driver_standings_partition(
    season: int,
    round_number: int,
    bucket: str,
    database_name: str,
) -> None:
    add_partition(
        table_name="driver_standings",
        partition_values=[str(season), str(round_number)],
        location=(
            f"s3://{bucket}/data_collected/driver_standings/"
            f"season={season}/round={round_number}/"
        ),
        database_name=database_name,
    )


def add_constructor_standings_partition(
    season: int,
    round_number: int,
    bucket: str,
    database_name: str,
) -> None:
    add_partition(
        table_name="constructor_standings",
        partition_values=[str(season), str(round_number)],
        location=(
            f"s3://{bucket}/data_collected/constructor_standings/"
            f"season={season}/round={round_number}/"
        ),
        database_name=database_name,
    )


def add_reference_partition(
    dataset: str,
    season: int,
    bucket: str,
    database_name: str,
) -> None:
    add_partition(
        table_name=dataset,
        partition_values=[str(season)],
        location=(
            f"s3://{bucket}/data_collected/"
            f"{dataset}/season={season}/"
        ),
        database_name=database_name,
    )