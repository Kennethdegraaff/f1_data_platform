import os

from f1_data.pipeline import run_pipeline


def lambda_handler(event: dict, context: object) -> dict:
    bucket = os.environ["F1_DATA_BUCKET"]

    run_pipeline(bucket=bucket)

    return {
        "statusCode": 200,
        "body": "F1 data pipeline completed successfully",
    }