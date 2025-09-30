# 🎯 Level 4 - Prefect Orchestration

This directory contains a **Prefect implementation** of the Piwik ETL process, showcasing tasks, flows, and S3 integration using [Prefect](https://prefect.io/) and its built-in utilities.

## ✨ Features

- **🧩 Task-based architecture**: Each ETL step is a separate Prefect task
- **🔄 Flow orchestration**: Main flow coordinates all tasks with proper error handling
- **☁️ S3 integration**: Uses `prefect-aws` for seamless S3 uploads
- **📅 Scheduling**: Built-in cron scheduling support
- **📊 Monitoring**: Rich logging and observability through Prefect UI

## 🚀 Quick Setup

By this point you should have enabled the `venv` and installed the requirements for the whole project.

### 1. Setup S3 Block

```bash
python prefect/s3.py
```

### 2. Run Flow Locally

```bash
python prefect/etl_flow.py
```

## 📊 Monitoring & UI

Access the **Prefect UI** to monitor:

- ✅ Flow runs and task status
- ⏱️ Execution times and performance  
- 📋 Logs and error details
- 📅 Scheduling and upcoming runs

**Start the Prefect server:**

```bash
prefect server start
```

**Then visit:** [http://localhost:4200](http://localhost:4200)

## 🚀 Production Deployment

You will see a demo script to deploy with daily scheduling:

```bash
python prefect/deploy.py
```

> You can leave the server open to see how this behaves when the schedule is due.