import os

from f1_data.pipeline import run_pipeline

if __name__ == "__main__":
    bucket = os.environ["F1_DATA_BUCKET"]

    run_pipeline(bucket=bucket)