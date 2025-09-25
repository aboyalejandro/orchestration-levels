# 🧭 Orchestration Levels: From Local to Cloud

This repo demonstrates **4 orchestration levels** for daily batch ETL, from simple local cron to full cloud orchestration. Each level uses the **same containerized ETL code** - only the scheduling mechanism changes.

> **Key principle:** "Orchestrators coordinate; containers compute." Keep heavy processing logic in containers, not in DAG tasks.

## Current Status: Level 1 & 2 Complete ✅

### Level 1: Local Cron 🕰️
**What:** Simple Python script + crontab scheduling
- Minimal ETL script (`main.py`) 
- Local virtual environment
- Cron job every 5 minutes
- Environment variables via `.env`

**Good for:** Proof of concept, single machine, development testing

### Level 2: GitHub Actions + Docker 🐙
**What:** Containerized ETL + GitHub Actions scheduler
- Dockerfile for reproducible environment
- GitHub Actions workflow (daily + manual trigger)
- Secrets management via GitHub Secrets
- Same ETL code, containerized

**Good for:** Small daily batches, simple CI/CD, container parity

### Level 3: ECR Registry + Lambda ☁️
**What:** Fully managed AWS scheduler + serverless execution
- ECR container image
- Lambda from container image
- EventBridge schedule trigger

**Good for:** < 15min jobs, serverless, auto-scaling

### Level 4: Full Orchestration (Airflow/Prefect) 🎯
**What:** Multi-step workflows with dependencies
- Prefect flow
- S3 Operator
- Python script
- Scheduling

**Good for:** Multi-step pipelines, complex dependencies, enterprise scale

## Decision Guide

- **Single daily job:** Level 1-2 (cron/GitHub Actions)
- **AWS + < 15min:** Level 3 (Lambda)
- **AWS + > 15min:** Level 4 (ECS tasks)
- **Complex workflows:** Level 5 (Airflow/Prefect)