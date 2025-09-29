# 🧭 Orchestration Levels: From Local CRON to Orchestrators

This repo demonstrates **4 orchestration levels** for daily batch ETL, from simple local cron to full cloud orchestration. Each level uses the **same containerized ETL code** - only the scheduling mechanism changes.

> **Key principle:** "Orchestrators coordinate; containers compute." Keep heavy processing logic in containers, not in DAG tasks.

## 📋 Prerequisites

To follow along, you'll need:

- **Docker Desktop** - For containerized deployments
- **Piwik PRO Demo Account** - [Get API credentials](https://help.piwik.pro/support/questions/generate-api-credentials/)
- **AWS Account** - With S3 bucket and IAM roles for ECR/S3 access - [Setup guide](https://docs.aws.amazon.com/AmazonECR/latest/userguide/image-push-iam.html)

## ⚡ Quick Start

1. **Setup environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your Piwik credentials
   ```

2. **Run with Docker:**
   ```bash
   # Build the image
   docker build -t piwik-etl .
   
   # Run with .env attached
   docker run --rm --env-file .env piwik-etl
   ```

## 🎯 Orchestration Levels

This project showcases **4 orchestration levels** for daily batch ETL, from simple local cron to full cloud orchestration. Each level uses the **same containerized ETL code** - only the scheduling mechanism changes.

> **Key principle:** "Orchestrators coordinate; containers compute." Keep heavy processing logic in containers, not in DAG tasks.

### 1️⃣ Level 1: Local Cron 🕰️
**What:** Simple Python script + crontab scheduling  
**Good for:** Proof of concept, single machine, development testing

1. **Be in project root:** `/your-path/orchestration-levels`
2. **Test script first:** 
   ```bash
   python -m venv venv
   source venv/bin/activate
   python main.py --local # Will export the files on piwik-data path
   ```
3. **Add to cron:** `crontab -e`
4. **In the cron editor (vi):**
   - Press `i` (insert mode)
   - Add this exact line:
   ```
   */5 * * * * /bin/bash -c "cd /your-path/orchestration-levels && source venv/bin/activate && python main.py"
   ```
   - Press `Esc`, type `:wq`, press Enter
5. **Verify:** `crontab -l`
6. **Check it works:** `ls -la piwik-data/` (after 5 minutes)
7. **Remove all cron jobs:** `crontab -r`

**Expected output:**

```bash
(venv) ➜  orchestration-levels git:(main) ✗ crontab -e
crontab: no crontab for your-user-name - using an empty one
crontab: installing new crontab
(venv) ➜  orchestration-levels git:(main) ✗ crontab -l
*/5 * * * * /bin/bash -c "cd Users/Desktop/your-user-name/orchestration-levels && source venv/bin/ activate && python main.py"
(venv) ➜  orchestration-levels git:(main) ✗ ls -la piwik-data/
total 0
drwxr-xr-x   4 your-user-name  staff  128 25 sep 20:23 .
drwxr-xr-x@ 17 your-user-name  staff  544 25 sep 20:23 ..
-rw-r--r--   1 your-user-name  staff    0 25 sep 20:20 .gitkeep
drwxr-xr-x   3 your-user-name  staff   96 25 sep 20:22 2021
(venv) ➜  orchestration-levels git:(main) ✗ 
```

**File permissions explained:**

- `drwxr-xr-x` = Directory permissions (d = directory, rwx = read/write/execute for owner, r-x = read/execute for group/others)
- `-rw-r--r--` = File permissions (- = regular file, rw- = read/write for owner, r-- = read-only for group/others)
- `4, 7, 1, 3` = Number of hard links
- `alejandroaboy staff` = Owner and group
- `128, 544, 0, 96` = File/directory size in bytes
- `Date/time` = Last modification time

### 2️⃣ Level 2: GitHub Actions + Docker 🐙
**What:** Containerized ETL + GitHub Actions scheduler  
**Good for:** Small daily batches, simple CI/CD, container parity

- **Scheduled execution**: Runs daily at 2 AM UTC (see `.github/workflows/etl.yml`)
- **Manual triggers**: Available in GitHub Actions tab
- **Secret management**: Configure your `.env` credentials as Action Secrets - [Setup guide](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets)

### 3️⃣ Level 3: ECR Registry + Lambda ☁️
**What:** Fully managed AWS scheduler + serverless execution  
**Good for:** < 15min jobs, serverless, auto-scaling

- **Container deployment**: Uses `.github/workflows/deploy.yml` to push Docker images to AWS ECR
- **Lambda integration**: Automatically deploys ECR images to Lambda functions
- **Serverless execution**: Runs on-demand with AWS Lambda's managed infrastructure

### 4️⃣ Level 4: Full Orchestration (Prefect) 🎯
**What:** Multi-step workflows with dependencies  
**Good for:** Multi-step pipelines, complex dependencies, enterprise scale

- **Advanced orchestration**: Full workflow engine with task dependencies and monitoring
- **Setup guide**: Follow `prefect/README.md` to enable the Prefect project
- **Features**: Rich UI, task retries, parallel execution, and observability

## 🏗️ Project Structure

```
orchestration-levels/
├── 📁 .github/workflows/     # CI/CD pipelines
│   ├── etl.yml              # GitHub Actions ETL
│   └── deploy.yml           # ECR deployment
├── 📁 prefect/              # Prefect workflow implementation
│   ├── etl_flow.py          # Main Prefect flow
│   ├── deploy.py            # Deployment script
│   ├── s3.py                # S3 block configuration
│   └── README.md            # Prefect setup guide
├── 📁 src/                  # Core ETL modules
│   ├── piwik.py            # Piwik API integration
│   ├── s3.py               # S3 utilities
│   └── local.py            # Local file operations
├── 🐳 Dockerfile           # Container configuration
├── 📝 main.py              # Main ETL script
├── 📋 requirements.txt     # Python dependencies
├── ⚙️ .env.example         # Environment template
└── 📚 README.md           # This file
```