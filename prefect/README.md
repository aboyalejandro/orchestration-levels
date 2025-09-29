# Prefect ETL Flow for Piwik Analytics

This directory contains a Prefect implementation of the Piwik ETL process, showcasing tasks, flows, and S3 integration using Prefect's built-in utilities.

## Features

- **Task-based architecture**: Each ETL step is a separate Prefect task
- **Flow orchestration**: Main flow coordinates all tasks with proper error handling
- **S3 integration**: Uses `prefect-aws` for seamless S3 uploads
- **Flexible storage**: Supports both local and S3 storage modes
- **Scheduling**: Built-in cron scheduling support
- **Monitoring**: Rich logging and observability through Prefect

## Project Structure

```
prefect/
├── etl_flow.py          # Main Prefect flow with tasks
├── deploy.py            # Deployment script with scheduling
├── s3.py                # S3 block configuration
├── requirements.txt     # Prefect dependencies
```

## Setup

By this point you should have enabled the `venv` and installed the requirements for the whole project.

1. **Setup S3 block** (for S3 uploads):
```bash
python prefect/s3.py
```

## Usage

### Run Flow Locally (Test Mode)

```bash
# Run with local storage for testing
python prefect/etl_flow.py
```

## Monitoring

Access the Prefect UI to monitor:
- Flow runs and task status
- Execution times and performance
- Logs and error details
- Scheduling and upcoming runs

Start the Prefect server:
```bash
prefect server start
```

Then visit: http://localhost:4200

### Deploy with Scheduling

```bash
# Deploy flow with daily scheduling
python deploy.py
```