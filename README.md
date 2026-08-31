# 🏎️ F1 Data Platform

An ongoing personal **Data Engineering project** for collecting,
processing, storing and querying Formula 1 data.

The platform collects data from the **Jolpica F1 API**, transforms it
into structured Parquet datasets and stores the data in **Amazon S3**.
The datasets are registered in the **AWS Glue Data Catalog** and can be
queried using **Amazon Athena**.

The project is continuously evolving as I explore and implement new
Data Engineering concepts and practices.

## 🏗️ Architecture

```mermaid
flowchart TD
    API["Jolpica F1 API"]

    EB["EventBridge Scheduler"]
    Lambda["AWS Lambda"]
    ECR["Amazon ECR"]
    Docker["Docker Container"]
    Pipeline["Python Data Pipeline"]

    S3["Amazon S3"]
    Glue["AWS Glue Data Catalog"]
    Athena["Amazon Athena"]
    Grafana["Grafana"]

    EB --> Lambda
    ECR -->|Container image| Lambda
    Lambda --> Docker
    Docker --> Pipeline

    API --> Pipeline
    Pipeline --> S3
    S3 --> Glue
    Glue --> Athena
    Athena --> Grafana
```

### CI/CD

```mermaid
flowchart LR
    GitHub["GitHub"]
    Actions["GitHub Actions"]
    Tests["pytest"]
    Docker["Docker Build"]
    ECR["Amazon ECR"]
    Lambda["AWS Lambda"]

    GitHub -->|Push to main| Actions
    Actions --> Tests
    Tests --> Docker
    Docker --> ECR
    ECR --> Lambda
```

GitHub Actions authenticates with AWS using **OIDC** and an IAM role,
avoiding the use of long-lived AWS credentials in GitHub.

## 🚀 Features

- Automated ingestion from the Jolpica F1 API
- Python-based data processing and transformation
- Parquet-based datasets
- Historical race and championship data
- Season and round based data partitioning
- Idempotent processing to avoid unnecessary reprocessing
- AWS Glue Data Catalog partition management
- SQL analytics through Amazon Athena
- Serverless execution with AWS Lambda
- Scheduled execution with EventBridge Scheduler
- Infrastructure as Code with Terraform
- Docker containerization
- CI/CD with GitHub Actions
- Automated testing with pytest

## 📊 Data

The platform currently processes several types of Formula 1 data:

| Dataset | Description |
| --- | --- |
| Races | Race calendar and event information |
| Drivers | Driver reference data |
| Constructors | Constructor/team reference data |
| Race results | Results from completed races |
| Sprint results | Results from completed sprint events |
| Driver standings | Historical driver championship standings |
| Constructor standings | Historical constructor championship standings |

Data is stored as Parquet files in Amazon S3 and registered in the
AWS Glue Data Catalog for querying through Amazon Athena.

## 📈 Data Visualization

The platform is also connected to Grafana for data visualization and
dashboarding.

The Grafana integration is currently being further developed, with a
focus on improving the dashboards and presenting the collected F1 data
more effectively.

## 🔄 Data Pipeline

The pipeline performs the following steps:

1. Resolve the target season.
2. Retrieve race, driver and constructor reference data.
3. Store reference data as Parquet datasets.
4. Process completed race results.
5. Process available sprint results.
6. Process historical driver standings.
7. Process historical constructor standings.
8. Store datasets in Amazon S3.
9. Register and maintain Glue Catalog partitions.

The pipeline is designed to be repeatable and safe to run multiple times.

Before processing a dataset, the pipeline checks whether the
corresponding Parquet object already exists. If it does, processing is
skipped while the corresponding Glue partition is still ensured.

This provides a basic form of **idempotent processing** and also allows
the pipeline to recover from cases where data was successfully written
but catalog registration was not completed.

## 🗂️ Project Structure

```text
.
├── infrastructure/
│   └── terraform/       # AWS infrastructure
├── lambda/
│   └── handler.py       # AWS Lambda entry point
├── src/
│   └── f1_data/
│       ├── catalog.py       # Glue Catalog operations
│       ├── jolpica.py       # Jolpica API client
│       ├── models.py        # Data models
│       ├── parsers.py       # API response parsing
│       ├── pipeline.py      # Pipeline orchestration
│       ├── storage.py       # S3 / Parquet storage
│       └── transformers.py  # Data transformations
├── tests/                # Automated tests
├── Dockerfile
├── run_pipeline.py       # Local pipeline entry point
└── pyproject.toml
```

## 🛠️ Tech Stack

### Programming & Data

- Python
- SQL
- Parquet
- pytest

### AWS

- Amazon S3
- AWS Glue Data Catalog
- Amazon Athena
- AWS Lambda
- EventBridge Scheduler
- Amazon ECR
- IAM

### Infrastructure & DevOps

- Terraform
- Docker
- GitHub Actions
- Git

## ☁️ Infrastructure

The AWS infrastructure is managed using **Terraform**.

The Terraform configuration currently manages resources including:

- Amazon S3
- AWS Lambda
- EventBridge Scheduler
- Amazon ECR
- IAM
- AWS Glue Data Catalog
- Amazon Athena

Infrastructure is version controlled alongside the application code,
allowing the cloud environment to be managed as Infrastructure as Code.

## 🐳 Docker

The data pipeline is packaged as a Docker container using the AWS Lambda
Python 3.12 base image.

The container image is built by GitHub Actions and pushed to Amazon ECR.
AWS Lambda then runs the containerized pipeline.

## 🔄 CI/CD

The project uses **GitHub Actions** for automated testing and deployment.

On every push to the `main` branch, the workflow:

1. Installs the Python dependencies
2. Runs the automated test suite
3. Authenticates with AWS using GitHub Actions OIDC
4. Builds the Docker image for AWS Lambda
5. Pushes the image to Amazon ECR
6. Updates the Lambda function to use the new image

This provides an automated path from a change in the GitHub repository
to a deployed version of the data pipeline.

## 🧪 Testing

The project includes automated tests covering the main components of
the data platform.

Tests are written with **pytest** and cover areas including:

- API client behaviour
- Data parsing
- Data transformation
- S3 storage
- Glue Catalog operations
- Pipeline processing

The test suite is automatically executed as part of the GitHub Actions
CI/CD workflow.

## 💻 Local Development

### Requirements

- Python 3.12+
- Docker
- Terraform
- AWS account

### Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Run tests

```bash
pytest
```

### Run the pipeline locally

```bash
python run_pipeline.py
```

AWS credentials and the required environment variables must be
configured when running the pipeline locally.

## 📌 Project Status

**Ongoing**

Current work includes:

- Expanding the data platform with additional datasets
- Improving pipeline reliability
- Further developing the AWS data architecture
- Expanding automated tests and CI/CD
- Adding comprehensive project documentation
- Improving the project README and architecture documentation

## 🎯 Project Goals

This project is both a practical portfolio project and a way to
continuously develop my Data Engineering skills.

The main areas of focus are:

- Data ingestion
- Data transformation
- Data pipelines
- Cloud data platforms
- Data lakes
- Infrastructure as Code
- Automation
- Testing and reliability
- Analytical data access
